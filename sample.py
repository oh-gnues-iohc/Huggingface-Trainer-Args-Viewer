from models.model import BiEncoder
from tqdm import tqdm
import torch
import torch.nn as nn
import torch.optim as optim
from transformers import AutoTokenizer, TrainingArguments, Trainer, HfArgumentParser
import logging
import os
from datasets import load_dataset, load_from_disk
from dataclasses import dataclass, field
from utils.data_collator import DataCollatorForResponseSelection
import transformers
from typing import Union

@dataclass
class ModelArguments:
    pretrained_model_name_or_path: str=field(
        default=""
    )
    use_auth_token: str=field(
        default="", metadata={"help": "비공개 모델 사용에 필요한 인증 토큰"}
    )

@dataclass
class DataArguments:
    data_name_or_path: str=field(
        default="squad_kor_v1"
    )
    use_auth_token_data: str=field(
        default=None, metadata={"help": "비공개 데이터 사용에 필요한 인증 토큰"}
    )
    train_split: str = field(
        default="train", metadata={"help": "학습 데이터 이름"}
    )
    eval_split: str = field(
        default="validation", metadata={"help": "평가 데이터 이름"}
    )
    shuffle: bool = field(
        default=True, metadata={"help": "데이터 셔플 여부"}
    )
    query_column_name: str = field(
        default="question", metadata={"help": "Query 모델의 입력 데이터 Column 이름"}
    )
    candidate_column_name: str = field(
        default="context", metadata={"help": "Candidate 모델의 입력 데이터 Column 이름"}
    )
    query_max_length: int = field(
        default=512, metadata={"help": "Query 모델의 최대 토큰 길이"}
    )
    candidate_max_length: int = field(
        default=512, metadata={"help": "Candidate 모델의 최대 토큰 길이"}
    )

@dataclass
class TrainArguments(TrainingArguments):
    output_dir: str = "runs/"
    do_train: bool = True
    do_eval: bool = False
    per_device_train_batch_size: int = 8
    per_device_eval_batch_size: int = 8
    num_train_epochs: float = 3.0
    evaluation_strategy: Union[transformers.trainer_utils.IntervalStrategy, str] = 'steps'

def main():
    parser = HfArgumentParser((ModelArguments, DataArguments, TrainArguments))
    model_args, data_args, train_args = parser.parse_args_into_dataclasses()

    model = BiEncoder.from_pretrained(**vars(model_args))
    tokenizer = AutoTokenizer.from_pretrained(**vars(model_args))

    if os.path.isdir(data_args.data_name_or_path):
        dataset = load_from_disk(data_args.data_name_or_path)
    else:
        dataset = load_dataset(data_args.data_name_or_path, use_auth_token=data_args.use_auth_token_data)

    if data_args.shuffle:
        dataset = dataset.shuffle()

    def example_function(examples):

        tokenized_query = tokenizer(
            examples[data_args.query_column_name],
            truncation=True,
            padding="max_length",
            max_length=data_args.query_max_length
        )

        tokenized_candidate= tokenizer(
            examples[data_args.candidate_column_name],
            truncation=True,
            padding="max_length",
            max_length=data_args.candidate_max_length
        )

        tokenized_inputs = {f"query_{k}": v for k, v in tokenized_query.items()}
        tokenized_inputs.update({f"candidate_{k}": v for k, v in tokenized_candidate.items()})

        return tokenized_inputs
    
    dataset = dataset.map(example_function, batched=True, remove_columns=dataset[data_args.train_split].column_names)

    data_collator = DataCollatorForResponseSelection(
        tokenizer=tokenizer,
    )

    def compute_metrics(p):
        predictions = p.predictions
        label_ids = p.label_ids
        return {"p": predictions}
    
    trainer = Trainer(
        model=model,
        args=train_args,
        tokenizer=tokenizer,
        data_collator=data_collator,
        compute_metrics=compute_metrics,
        train_dataset=dataset[data_args.train_split],
        eval_dataset=dataset[data_args.eval_split],
    )

    trainer.train()


if __name__ == "__main__":
    main()
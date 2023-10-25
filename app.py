from srcs.finder import DataclassFinder
import streamlit as st

command = {}
setter = {"str": str, "int": int, "float": float, "bool": bool}


def main():
    uploaded_file = st.file_uploader("Choose a Python file", accept_multiple_files=False)
    if uploaded_file:
        for dataclass in DataclassFinder(uploaded_file.read()):
            st.markdown(f"#### {dataclass['name']}")
            st.markdown("---")
            for element in dataclass["elements"]:
                command[element['name']] = st.text_input(f"{element['name']}: ", f"{element['default'] if element['default'] else ''}", help=f"type: {element['type']}\n\n{element['help'] if element['help'] else ''}")
            st.markdown("---")

        st.write(command)

if __name__ == "__main__":
    main()

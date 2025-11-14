# file: hello_modal.py
import modal

app = modal.App("hello-world")

@app.function()
def say_hello(name: str):
    return f"Hello, {name} from Modal!"

@app.local_entrypoint()
def main():
    print(say_hello.remote("Mariam"))

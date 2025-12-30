# Skir Python example

Example showing how to use skir's [Python code generator](https://github.com/gepheum/skir-python-gen) in a project.

## Build and run the example

```shell
# Download this repository
git clone https://github.com/gepheum/skir-python-example.git

cd skir-python-example

# Run Skir-to-Python codegen
npx skir gen

python snippets.py
```

### Start a skir service

From one process, run:
```shell
python start_service.py
```

From another process, run:
```shell
python call_service.py
```

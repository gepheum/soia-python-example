# Soia Python example

Example showing how to use soia's [Python code generator](https://github.com/gepheum/soia-python-gen) in a project.

## Build and run the example

```shell
# Download this repository
git clone https://github.com/gepheum/soia-python-example.git

cd soia-python-example

# Install all dependencies, which include the soia compiler and the soia
# typescript code generator
npm i

npm run snippets
# Same as:
#   npm run build  # .soia to .py codegen
#   python snippets.py
```

### Start a soia service

From one process, run:
```shell
npm run start-service
#  Same as:
#    npm run build
#    python start_service.py
```

From another process, run:
```shell
npm run call-service
#  Same as:
#    npm run build
#    python call_service.py
```

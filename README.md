# GlassFlow Pipelines Repository Template

The purpose of this repo is to showcase how to write and maintain GlassFlow pipelines in production.

## Repo Structure

```
pipelines/
   pipeline_1/
      pipeline.yaml                 -- Pipeline configuration
      transformations/              -- Directory with pipeline trasformation 
         transformation_1/
            handler.py
            requirements.txt

tests/
    pipeline_1/
        test_transformation_1.py    -- Unit test for trasformation 1
        test_pipeline_1.py          -- integration test for pipeline 1 (use SDK to test already created pipeline)

.github/
   workflows/
```

## Pipeline YAML specification 


```yaml
name:
pipeline_id: # if not defined, pipeline will be created by CI/CD
space_id:

components:
  - id: my_source
    name: My Source
    type: source
    kind: 
    config_secret_ref:
    
  - id: my_transformer
    name: My transformer # default: <id>
    type: transformer
    requirements:
      path:
    handler:
      path:
    inputs:
      - my_source
    
  - id: my_sink
    name: My sink
    type: sink
    kind:
    config_secret_ref:
    inputs:
      - my_transformer
```

> [!NOTE]  
> A pipeline consists on three components: source, transformer and sink


### Pipeline Components

A component represents the smallest work unit at GlassFlow. They consist of an input queue, some python code and output channels.

#### Transformer

This type of component consist of one input and one output and a python code:

```yaml
  - id:
    name:
    type: transformer
    inputs:
      - <component_id>    # Component ID to pull events from
    env_vars:
      - name:
        value:
    requirements:
      path:               # path to file with requirements.txt file relative to pipeline yaml file
      value:              # requirements.txt file value
    transformation:
      path:               # path to python handler file relative to pipeline yaml file 
      value:
    files:                # [Not in v1]
      - name:
        value:            # Code
        path:             # path to file with code
```

#### Source

Source component

```yaml
  - id:
    name:
    type: source
    kind:
    config:
```

#### Sink

Sink component

```yaml
  - id:
    name:
    type: sink
    kind:
    config:
    inputs:
      - <component_id>    # Component ID to pull events from
```
# GlassFlow in Production

## Repo Structure

```
glassflow.yaml                 -- Glassflow configuration file

pipelines/
   pipeline-x/
      pipeline.yaml            -- Pipeline configuration
      common/                  -- Directory with common python code shared by all the steps
      functions/               -- Directory with pipeline functions (folder name == function_id) 
         function-x/
            handler.py
            requirements.txt

tests/
   pipelines/
      pipeline_x/
         test_step_x.py        -- Unit test for step x
         test_pipeline_x.py    -- integration test for pipeline x (use SDK to test already created pipeline)

.github/
   workflows/
```

## Pipeline YAML specification 


```yaml
name:
pipeline_id: # if not defined, pipeline will be created by CI/CD
space_id:

source:
  kind:
  config:

sink:
  kind:
  config:

environment:
  - name:
    value:
    
functions:
  - id:
    name: # default: <id>
    requirements: # default: steps/<step_id>/requirements.py
    handler: # default: steps/<step_id>/handler.py
    inputs:
      - type: # default: sequential
        config:
    
    outputs:
      - type: # default: sequential
        config:

```

### Type of Inputs

#### Sequential

This is the default input type. If not provided in the YAML, we will assume the
functions input is the previous function from the list of functions in the YAML 
(or the source if it's the first function).

```yaml
functions:
  - id: step_1
    name: Step 1
  - id: step_2
    name: Step 2
    input:
      - type: sequential
        config:
          id: step_1
```

#### Merge

This input type will merge events from multiple functions.

```yaml
functions:
  - id: step_1
    name: Step 1
  - id: step_2
    name: Step 2
  - id: step_3
    name: Step 3
    inputs:
      - type: merge
        config:
          steps:
            - step_1
            - step_2
```

Step 3 will receive the combined output of steps 1 and 2:

```json
{
  "req_id": 123,
  "steps": {
    "step_1": {},
    "step_2": {}
  }
}
```

### Outputs

#### Sequential

This is the default output type. If not provided in the YAML, we will assume the
functions output is the next function from the list of functions in the YAML 
(or the sink if it's the last function).

```yaml
functions:
  - id: step_1
    name: Step 1
  - id: step_2
    name: Step 2
    outputs:
      - type: sequential
        config:
          id: step_1
```

#### Branching

```yaml
functions:
  - id: step_1
    name: Step 1
    outputs:
      - type: branch
        config:
          branches:
            - id: step_2
              key: name
              value: 3
              operation: eq
            - id: step_3
              key: name
              value: 3
              operation: gt
            - id: step_4
              key: name
              operation: is_null
  - id: step_2
    name: Step 2
  - id: step_3
    name: Step 3
  - id: step_4
    name: Step 4
```

### Multiple inputs and outputs

Each function can consume events from multiple inputs and publish them to multiple outputs (replicate events and send them to different outputs).

## GlassFlow YAML specification

Probably not yet needed as we don't have many global settings. 

```yaml
organization_id:
```

# GlassFlow in Production

## Repo Structure

```
glassflow.yaml                 -- Glassflow configuration file
secrets.yaml                 -- Encrypted file with secrets (CI/CD will set the secrets on the GF secrets manager)
pipelines/
   pipeline_x/
      pipeline.yaml            -- Pipeline configuration
      common/                  -- Directory with common python code shared by all the steps
      components/                  -- Directory with pipeline components (folder name == component_id) 
         component_x/
            handler.py
            requirements.txt

tests/
    pipeline_x/
        test_component_x.py     -- Unit test for component x
        test_pipeline_x.py      -- integration test for pipeline x (use SDK to test already created pipeline)

.github/
   workflows/
```

## Pipeline YAML specification 


```yaml
name:
pipeline_id: # if not defined, pipeline will be created by CI/CD
space_id:

common_modules: # Path to python modules to load into all functions [Not in v1]
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

### Restrictions

- A pipeline can only have one source and one sink (for now)
- The graph of functions can not have any cycle
- Components without output are allowed but will trigger a warning
- Components without input are not possible

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
        value_secret_ref: # Key to secret
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

#### Branch

This block type, sends the events to different blocks depending on a list of conditions.

```yaml
  - id:
    name:
    type: branch
    inputs:
      - <component_id>    # Component ID to pull events from
    branches:
      - branch_id:
        conditions:
          - key:
            operator:
            value:
            dtype:
```
#### Filter

This block filters out events between blocks:

```yaml
  - id:
    name:
    type: filter
    inputs:
      - <component_id>    # Component ID to pull events from
    conditions:
      - key:
        operator:
        value:
        dtype:
```

#### Source

Source block

```yaml
  - id:
    name:
    type: source
    kind:
    config:
    config_secret_ref:  # Key of secret to load the config from 
```

#### Sink

Sink block

```yaml
  - id:
    name:
    type: sink
    kind:
    config:
    config_secret_ref:  # Key of secret to load the config from
    inputs:
      - <component_id>    # Component ID to pull events from
```

### Examples

#### Sequential pipeline with filtering block

```yaml
name:
pipeline_id: # if not defined, pipeline will be created by CI/CD
space_id:
    
blocks:
  - id: my_postgres
    name: My Postgres Source
    type: source
    kind: postgres
    config_secret_ref:
    
  - id: my_transformer_1
    name: My transformer 1 # default: <id>
    type: transformer
    requirements:
      path:
    handler:
      path:
    inputs:
      - my_postgres
    
  - id: my_filter
    name: My filter # default: <id>
    type: filter
    conditions:
      - key: num_messages
        operator: ge
        value: 5
        dtype: int
    inputs:
      - my_transformer_1
    
  - id: my_transformer_2
    name: My transformer 2 # default: <id>
    type: transformer
    requirements:
      path:
    handler:
      path:
    inputs:
      - my_filter
    
  - id: my_sink
    name: My sink
    type: sink
    kind: webhook
    config_secret_ref:
    inputs:
      - my_transformer_2
```

```mermaid
---
Sequential pipeline with filtering block
---
flowchart LR
    source@{ shape: lean-r, label: "Source" }
    sink@{ shape: lean-l, label: "Sink" }
    fn_1@{ shape: rounded, label: "My transformer 1" }
    filter@{ shape: hex, label: "Filter:\nkey **num_messages** >= 5" }
    fn_2@{ shape: rounded, label: "My transformer 2" }
    
    source --> fn_1 --> filter --> fn_2 --> sink
```

#### Complex pipeline

```yaml
name:
pipeline_id: # if not defined, pipeline will be created by CI/CD
space_id:
    
components:
  - id: my_postgres
    name: My Postgres Source
    type: source
    kind: postgres
    config_secret_ref:
    
  - id: my_transformer_1
    name: My transformer 1 # default: <id>
    type: transformer
    requirements:
      path:
    handler:
      path:
    inputs:
      - my_postgres
    
  - id: my_branch
    name: Branch # default: <id>
    type: branch
    inputs:
      - my_transformer_1
    branches:
      - block_id: branch_1
        conditions:
          - key: num_messages
            operator: ge
            value: 5
            dtype: int
      - block_id: branch_2
        conditions:
          - key: num_messages
            operator: lt
            value: 5
            dtype: int
      - block_id: branch_3
        conditions:
          - key: num_messages
            operator: is_null
            dtype: int
    
  - id: my_transformer_2
    name: My transformer 2 # default: <id>
    type: transformer
    requirements:
      path:
    handler:
      path:
    inputs:
      - branch_1
    
  - id: my_transformer_3
    name: My transformer 3 # default: <id>
    type: transformer
    requirements:
      path:
    handler:
      path:
    inputs:
      - branch_2
    
  - id: my_transformer_4
    name: My transformer 4 # default: <id>
    type: transformer
    requirements:
      path:
    handler:
      path:
    inputs:
      - branch_3

  - id: my_sink
    name: My sink
    type: sink
    kind:
    config_secret_ref:
    inputs:
      - my_transformer_2
      - my_transformer_3 
      - my_transformer_4 
```

```mermaid
---
Branching Example
---
flowchart LR
    
    source@{ shape: lean-r, label: "Source" }
    sink@{ shape: lean-l, label: "Sink" }
    fn_1@{ shape: rounded, label: "Transformation 1" }
    cond@{ shape: diamond, label: "Conditional" }
    fn_2@{ shape: rounded, label: "Transformation 2" }
    fn_3@{ shape: rounded, label: "Transformation 3" }
    fn_4@{ shape: rounded, label: "Transformation 4" }
    
    source --> fn_1 --> cond
    cond --"`key **num_messages** >= 5`"--> fn_2 --> sink
    cond --"`key **num_messages** < 5`"--> fn_3 --> sink
    cond --"`key **num_messages** is null`"--> fn_4 --> sink
```

## GlassFlow YAML specification

Probably not yet needed as we don't have many global settings. 

```yaml
organization_id:
```

## Secrets

Secrets will be stored in our glassflow secret store, the SDK will set the secrets from the `secrets.yaml` file 
which will be encrypted when pushed to github.

Secrets are referenced in the YAML files by their keys.
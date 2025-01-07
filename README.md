# GlassFlow in Production

## Repo Structure

```
glassflow.yaml                 -- Glassflow configuration file
secrets.yaml                 -- Encrypted file with secrets (CI/CD will set the secrets on the GF secrets manager)
pipelines/
   pipeline_x/
      pipeline.yaml            -- Pipeline configuration
      common/                  -- Directory with common python code shared by all the steps
      blocks/                  -- Directory with pipeline blocks (folder name == block_id) 
         block_x/
            handler.py
            requirements.txt

tests/
    pipeline_x/
        test_block_x.py        -- Unit test for step x
        test_pipeline_x.py    -- integration test for pipeline x (use SDK to test already created pipeline)

.github/
   workflows/
```

## Pipeline YAML specification 


```yaml
name:
pipeline_id: # if not defined, pipeline will be created by CI/CD
space_id:

common_modules: # Path to python modules to load into all functions
blocks:
  - id: my_source
    name: My Source
    type: source
    kind: 
    config_secret_ref:
    next_block_id: my_transformer
    
  - id: my_transformer
    name: My transformer # default: <id>
    type: transformer
    requirements: # default: blocks/<block_id>/requirements.py
    handler: # default: blocks/<block_id>/handler.py
    next_block_id: sink
    
  - id: my_sink
    name: My sink
    type: sink
    kind:
    config_secret_ref:
```

### Restrictions

- A pipeline can only have one source and one sink (for now)
- The graph of functions can not have any cycle
- Blocks without output are allowed but will trigger a warning
- Blocks without input are not possible

### Blocks

A block represents the smallest work unit at GlassFlow. They consist of an input queue, some python code and output channels.

#### Transformer

This type of block consists of one input and one output and a python code:

```yaml
  - id:
    name:
    type: transformer
    next_block_id:
    env_vars:
      - name:
        value:
        value_secret_ref:  # Key to secret
    requirements:
        path:   # path to file with requirements.txt file
        value:  # requirements.txt file value
    files:
      - name:
        value:  # Code
        path:   # path to file with code
```

#### Branch

This block type, sends the events to different blocks depending on a list of conditions.

```yaml
  - id:
    name:
    type: branch
    branches:
      - block_id:
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
    next_block_id:
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
    next_blok_id:
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
    next_block_id: my_transformer_1
    
  - id: my_transformer_1
    name: My transformer 1 # default: <id>
    type: transformer
    requirements: # default: blocks/<block_id>/requirements.py
    handler: # default: blocks/<block_id>/handler.py
    next_block_id: my_filter
    
  - id: my_filter
    name: My filter # default: <id>
    type: filter
    conditions:
      - key: num_messages
        operator: ge
        value: 5
        dtype: int
    next_block_id: my_transformer_2
    
  - id: my_transformer_2
    name: My transformer 2 # default: <id>
    type: transformer
    requirements: # default: blocks/<block_id>/requirements.py
    handler: # default: blocks/<block_id>/handler.py
    next_block_id: my_sink
    
  - id: my_sink
    name: My sink
    type: sink
    kind: webhook
    config_secret_ref:
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
    
blocks:
  - id: my_postgres
    name: My Postgres Source
    type: source
    kind: postgres
    config_secret_ref:
    next_block_id: my_transformer_1
    
  - id: my_transformer_1
    name: My transformer 1 # default: <id>
    type: transformer
    requirements: # default: blocks/<block_id>/requirements.py
    handler: # default: blocks/<block_id>/handler.py
    next_block_id: my_branch
    
  - id: my_branch
    name: Branch # default: <id>
    type: branch
    branches:
      - block_id: my_transformer_2
        conditions:
          - key: num_messages
            operator: ge
            value: 5
            dtype: int
      - block_id: my_transformer_3
        conditions:
          - key: num_messages
            operator: lt
            value: 5
            dtype: int
      - block_id: my_transformer_4
        conditions:
          - key: num_messages
            operator: is_null
            dtype: int
    
  - id: my_transformer_2
    name: My transformer 2 # default: <id>
    type: transformer
    requirements: # default: blocks/<block_id>/requirements.py
    handler: # default: blocks/<block_id>/handler.py
    next_block_id: my_sink
    
  - id: my_transformer_3
    name: My transformer 3 # default: <id>
    type: transformer
    requirements: # default: blocks/<block_id>/requirements.py
    handler: # default: blocks/<block_id>/handler.py
    next_block_id: my_sink
    
  - id: my_transformer_4
    name: My transformer 4 # default: <id>
    type: transformer
    requirements: # default: blocks/<block_id>/requirements.py
    handler: # default: blocks/<block_id>/handler.py
    next_block_id: my_sink

  - id: my_sink
    name: My sink
    type: sink
    kind:
    config_secret_ref:
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
# terraform-cloud-run-action

GitHub action for triggering Terraform Cloud runs

Workflow with the action usage example:

```
jobs:
  release:
    steps:
    # ...
    - name: Checkout commit
      uses: neuro-inc/upload-image-action@v21.9.3
      with:
        token: ${{ secrets.TF_API_TOKEN }}
        workspace: control-plane-dev
        variables:
          service_version=1.2.3
```


Arguments:

`token` -- secret Terraform Cloud token, pass: `${{ secrets.TF_API_TOKEN }}`.
`organization` -- Name of the Terraform Cloud organization, default: apolo-us.
`workspace` -- Name of the Terraform Cloud workspace.
`variables` -- Terraform Cloud workspace variables. Variables must exist in Terraform Cloud. Multiple variables can be passed, each on a separate line.

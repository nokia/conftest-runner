# conftest-runner

Tools is a glue between [conftest](https://github.com/open-policy-agent/conftest) and the [Gatekeeper](https://github.com/open-policy-agent/gatekeeper).
It allows verifying Kubernetes objects against Gatekeeper constraints.
The Kubernetes objects and the Gatekeeper constraints can be in a Helm chart form.
Verification can be run in Continuous Integration (CI/CD) pipelines without the Kubernetes cluster access or even the Gatekeeper.

conftest-runner performs the following steps:
- templates Helm chart, to get Kubernetes objects manifests
- convert each templated Kubernetes object to AdmissionReview object (consumed by the Gatekeeper)
- templates Gatekeeper constraint templates Helm chart
- templates Gatekeeper constraints Helm chart
- extract Rego code from the Gatekeeper constraints
- transform extract Rego code into conftest tests
- run conftest

Required dependencies:
- installed [Helm](https://helm.sh/) (Helm 3 preferred)
- installed [conftest](https://github.com/open-policy-agent/conftest)
- installed [Python 3](https://www.python.org/)
- installed additional Python packages like `pyyaml`
    - Run `python3 -m pip install -r requirements.txt` to install it.

## Usage scenarios

### Verify example Gatekeeper constraints

Clone [Gatekeeper](https://github.com/open-policy-agent/gatekeeper) repository (or download just Gatekeeper [examples](https://github.com/open-policy-agent/gatekeeper/tree/master/example) directory)

```
python3 src/conftest-runner.py \
    --input-kubernetes-objects ../gatekeeper/example/resources/bad_pod_namespaceselector.yaml \
    --policy-constraint-templates ../gatekeeper/example/templates/k8srequiredlabels_template.yaml \
    --policy-constraints ../gatekeeper/example/constraints/all_pod_must_have_gatekeeper_namespaceselector.yaml \
    --input-namespaces-file ../gatekeeper/example/resources/bad_ns_namespaceselector.yaml
```

## Helm installation

### From Homebrew (macOS/Linux)
```console
brew install helm
```
### From Chocolatey (Windows)
```console
choco install kubernetes-helm
```
### Add to PATH (Windows)

1. Download https://get.helm.sh/helm-canary-windows-amd64.zip
2. Unpack 
3. Add the path to unpacked folder to PATH in Environment Variables.

### From Apt (Debian/Ubuntu)
```console
curl https://baltocdn.com/helm/signing.asc | sudo apt-key add -
sudo apt-get install apt-transport-https --yes
echo "deb https://baltocdn.com/helm/stable/debian/ all main" | sudo tee /etc/apt/sources.list.d/helm-stable-debian.list
sudo apt-get update
sudo apt-get install helm
```

## Conftest installation

### Download from source (macOS/Linux)
Check desire version on https://github.com/open-policy-agent/conftest/releases.
In example is used 0.24.0 version.
```console
wget https://github.com/open-policy-agent/conftest/releases/download/v0.24.0/conftest_0.24.0_Linux_x86_64.tar.gz
tar xzf conftest_0.24.0_Linux_x86_64.tar.gz
sudo mv conftest /usr/local/bin
```

### From Homebrew (macOS/Linux)
```console
brew install conftest
```

### Add to PATH (Windows)

1. Download desired version from https://github.com/open-policy-agent/conftest/releases.
2. Unpack.
3. Add the path to unpacked folder to PATH in Environment Variables.

## Running tests

1. Install pytest
```console
pip install -U pytest
```

2. Go to conftest-runner repo root directory and run:
```console
pytest
```
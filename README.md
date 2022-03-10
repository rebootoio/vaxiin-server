<div id="top"></div>
<div align="center">
  <h1 align="center">Vaxiin Server</h1>

  <p align="center">
    Server side component of the Vaxiin framework
    <br />
    <a href="https://docs.vaxiin.io"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/rebootoio/vaxiin-server/issues/new?assignees=&labels=bug&template=bug_report.md&title=">Report Bug</a>
    ·
    <a href="https://github.com/rebootoio/vaxiin-server/issues/new?assignees=&labels=enhancement&template=feature_request.md&title=">Request Feature</a>
  </p>
    <a >
    <img src='https://img.shields.io/github/v/tag/rebootoio/vaxiin-server?style=for-the-badge'>
  </a>
  <a href='https://discord.gg/aEJ6qwcCGs'>
    <img src='https://img.shields.io/discord/813371439469297674?style=for-the-badge'>
  </a>
  <a href='https://github.com/rebootoio/vaxiin-server/blob/main/LICENSE'>
    <img src='https://img.shields.io/github/license/rebootoio/vaxiin-server?style=for-the-badge'>
  </a>
</div>

## Quick Start Guide
To get started quickly with all the component, follow the guide at the [sandbox repository](https://github.com/rebootoio/vaxiin-sandbox)


## Components
| Component | Repoistory | Artifact | Documentation |
|-----------|------------|----------|------|
| Server | [GitHub](https://github.com/rebootoio/vaxiin-server) | [DockerHub](https://hub.docker.com/repository/docker/rebooto/vaxiin-server) | [Docs](https://docs.vaxiin.io/configuration/server) |
| Handler | [GitHub](https://github.com/rebootoio/vaxiin-handler) | [DockerHub](https://hub.docker.com/repository/docker/rebooto/vaxiin-handler) | [Docs](https://docs.vaxiin.io/configuration/handler) |
| Agent | [GitHub](https://github.com/rebootoio/vaxiin-agent) | [DockerHub](https://hub.docker.com/repository/docker/rebooto/vaxiin-agent) | [Docs](https://docs.vaxiin.io/configuration/agent) |
| CLI | [GitHub](https://github.com/rebootoio/vaxctl)| [Release](https://github.com/rebootoio/vaxctl/releases) | [Docs](https://docs.vaxiin.io/configuration/cli) |

## Running
### Default Configuration
To run the server with default configuration and the **database in the current directory**:
```
docker run -d -v $(pwd):/db rebooto/vaxiin-server
```
### Custom configuration
Download the sample configuration file locally
```
wget https://raw.githubusercontent.com/rebootoio/vaxiin-server/main/config-example.yaml -O config.yaml
```
Edit the file, change configuration if needed and run the server
```
docker run -d -v $(pwd):/db -v $(pwd)/config.yaml:/etc/vaxiin-server-config/config.yaml rebooto/vaxiin-server
```
_Additional information about the available configuration can be found in the [docs](https://docs.vaxiin.io/configuration/server)._

## Builiding
The docker image can be built by cloning this repository and running `make build`\

## Contributing

Contributions are what make the Open Source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**!

If you have a suggestion that would make this better, please fork the repo and create a Pull Request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request


## License
Distributed under the [AGPL-3.0 License](https://github.com/rebootoio/vaxiin-server/blob/main/LICENSE) License.

## Contact
[Join the Rebooto Discord Server](https://discord.gg/aEJ6qwcCGs)

[Open an issue](https://github.com/rebootoio/vaxiin-server/issues)

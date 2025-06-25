# Yocto-Based Automotive Infotainment Image for Raspberry Pi 4

Welcome to the **Graduation-Project-Automotive-ECE25** Yocto repository. This project defines a custom Yocto build environment—complete with a bespoke layer—to generate a streamlined, automotive-grade Linux image for the Raspberry Pi 4. Whether you’re prototyping an in-vehicle infotainment (IVI) system, experimenting with CAN-bus integration, or simply exploring embedded Linux, this repo provides a solid scaffold.

---

## Table of Contents

1. [Repository Overview](#repository-overview)  
2. [Prerequisites](#prerequisites)  
3. [Repository Layout](#repository-layout)  
4. [Getting Started](#getting-started)  
5. [Configuring the Build](#configuring-the-build)  
6. [Building Your Image](#building-your-image)  
7. [Flashing & Testing](#flashing--testing)  
8. [Custom Layer: `meta-assem`](#custom-layer-meta-assem)  
9. [Adding New Recipes](#adding-new-recipes)  
10. [Troubleshooting & Tips](#troubleshooting--tips)  
11. [Roadmap & Contributing](#roadmap--contributing)  
12. [License](#license)  

---

## Repository Overview

This Yocto project brings together:

- **Poky** (Yocto Project Reference Distro)  
- **meta-raspberrypi** layer for Pi-specific kernels and firmware  
- **meta-openembedded** (optional) for extended packages  
- **meta-assem** – your custom automotive layer containing UI, middleware, and vehicle-interface recipes  
- A single, opinionated `local.conf` optimized for parallel builds, sstate-caching, and Pi 4 target machine  

_This repo does _not_ bundle Poky itself_. Instead, it exposes configuration and layers that you clone alongside Poky._

---

## Prerequisites

Before you begin, ensure you have:

- **Host OS**: Ubuntu 20.04 LTS (or equivalent Debian-based distro)  
- **Tools & Libraries** (install via `sudo apt-get install`):  
  - `git`  
  - `chrpath`, `diffstat`, `gawk`, `socat`, `cpio`  
  - `python3`, `python3-pip`  
  - `gcc`, `g++`, `make`, `libncurses5-dev`  
  - `texinfo`, `xz-utils`, `zip`, `unzip`, `openssl`  
- **Disk Space**: ≥ 50 GB free for downloads, build, and sstate cache  

---

## Repository Layout

```text
.
├── raspberrypi4/conf/
│   ├── bblayers.conf       # Yocto layers list
│   └── local.conf          # Build settings (MACHINE, parallelism, proxies)
├── meta-assem/             # Custom automotive Yocto layer
│   ├── conf/distro
│   │   └── adas.conf       # Custom distribution
│   └── recipes-*/          # Custom recipes (UI, middleware, utils)
├── .gitignore
└── README.md               # This file
```

- **`conf/`**: Defines which layers to include, machine target, network mirrors, and build flags.  
- **`meta-assem/`**: Houses everything special to your graduation project—images, recipes, and configuration fragments.

---

## Getting Started

1. **Clone Poky**  
   ```bash
   git clone -b kirkstone git://git.yoctoproject.org/poky.git
   cd poky
   ```

2. **Clone Layers**  
   In the same workspace:
   ```bash
   git clone git://git.openembedded.org/meta-openembedded
   git clone git://github.com/agherzan/meta-raspberrypi.git
   git clone https://github.com/Graduation-Project-Automotive-ECE25/Yocto.git yocto-project
   ```

3. **Initialize Build Environment**  
   ```bash
   source oe-init-build-env build
   ```

---

## Configuring the Build

Navigate into your new `build/` directory. Inside `conf/`, you’ll find:

- **`bblayers.conf`**: Add your layers here:
  ```ini
  BBLAYERS ?= " \
    ${TOPDIR}/../poky/meta \
    ${TOPDIR}/../poky/meta-poky \
    ${TOPDIR}/../meta-openembedded/meta-oe \
    ${TOPDIR}/../meta-openembedded/meta-python \
    ${TOPDIR}/../meta-raspberrypi \
    ${TOPDIR}/../yocto-project/meta-assem \
  "
  ```

- **`local.conf`**: Key settings to review:
  ```ini
  MACHINE = "raspberrypi4"
  BB_NUMBER_THREADS = "${@oe.utils.cpu_count()}"
  PARALLEL_MAKE = "-j${@oe.utils.cpu_count()}"
  SSTATE_DIR ?= "${TOPDIR}/../sstate-cache"
  DL_DIR ?= "${TOPDIR}/../downloads"
  CONF_VERSION = "1"
  # Uncomment to enable ccache
  # INHERIT += "ccache"
  # ENABLE UART or CAN specifics via DISTRO_FEATURES
  ```

_Tip:_ Adjust `MACHINE` to match your target hardware, e.g., `raspberrypi4-64`.

---

## Building Your Image

1. **Clean previous builds (optional)**  
   ```bash
   bitbake -c cleanall core-image-minimal
   ```

2. **Build the base image**  
   ```bash
   bitbake core-image-minimal
   ```
   Or build your custom image recipe (e.g., `my-ivi-image`):
   ```bash
   bitbake my-ivi-image
   ```

Artifacts appear in:
- `tmp/deploy/images/raspberrypi4/` (SD card-ready `.wic` or `.sdimg`)
- `tmp/deploy/rpms/` for individual packages

---

## Flashing & Testing

1. **Write image to SD card**  
   ```bash
   sudo dd if=tmp/deploy/images/raspberrypi4/core-image-minimal-raspberrypi4.wic \
     of=/dev/sdX bs=4M conv=fsync status=progress
   ```

2. **Boot your Pi**  
   Insert the card, apply 5 V/3 A power, and watch UART (115200 bps) or HDMI for console output.

3. **Login**  
   Default credentials for `core-image-minimal`:  
   - User: `root`  
   - No password (setshell or inject via `passwd` in your recipe)

---

## Custom Layer: `meta-assem`

This layer encapsulates:

- **Custom recipes** under `recipes-*/`  
- **Image definitions**, e.g., `recipes-images/my-ivi-image/my-ivi-image.bb`  
- **Configuration fragments** (`.bbappend`) for tuning third-party packages  
- **Distro features** (CAN bus, Qt, GPU acceleration)

Layer metadata is defined in `meta-assem/conf/layer.conf`. Increase its priority if you need to override core recipes.

---

## Adding New Recipes

1. **Create directory** in `meta-assem/recipes-<category>/your-recipe/`  
2. **Write `<your-recipe>.bb`**:
   ```bitbake
   SUMMARY = "Example widget daemon"
   LICENSE = "MIT"
   SRC_URI = "git://github.com/you/widget.git;branch=main"
   inherit cmake pkgconfig
   ```
3. **Include in your image**:
   ```bitbake
   IMAGE_INSTALL_append = " widget-daemon"
   ```

---

## Troubleshooting & Tips

- **Dependency errors**: Verify your layer priorities and `inherit` statements.  
- **Fetch failures**: Check proxy, `DL_DIR`, and URL spellings.  
- **Build stalls**: Enable verbose logs: `bitbake -v -D <recipe>`.  
- **Space issues**: Prune old sstate with `rm -rf sstate-cache/*`.

_For deeper dives, consult the [Yocto Project Mega-Manual](https://www.yoctoproject.org/docs/)._

---

## Roadmap & Contributing

Planned enhancements:

- Full Qt5/Qt6-based IVI UI with touchscreen calibration  
- CAN diagnostics integration using SocketCAN  
- In-vehicle encryption module with TPM support  

Contributions are welcome! Fork, open an issue, or submit a pull request. Please follow our [CONTRIBUTING.md](CONTRIBUTING.md) guidelines.

---

## License

This repository is released under the **MIT License**. See [LICENSE](LICENSE) for details.  
```

— Happy building! If you run into any blockers or want to integrate new automotive features (CAN, LIN, FlexRay, TPM), let me know and we can dive deeper.

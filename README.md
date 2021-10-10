# CAMouse

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
![](https://img.shields.io/github/stars/pandao/editor.md.svg) ![](https://img.shields.io/github/forks/pandao/editor.md.svg) ![](https://img.shields.io/github/tag/pandao/editor.md.svg) ![](https://img.shields.io/github/release/pandao/editor.md.svg) ![](https://img.shields.io/github/issues/pandao/editor.md.svg)

## Description

CAMouse uses camera to control a mouse with hand gestures. Hand gestures are processed using AI to enable basic mouse functionality. CAMouse uses only a CPU and isn't resource intensive.

## Installation

- Python 3.8

Requirements:

> pip install -r requirements.txt

## Running

Run with:

> python CAMouse.py

List of available options that enable debugging and custom setup can be viewied with --help or -h flag:

> python CAMouse.py -h

##Usage

App is tracking an index finger tip for cursor movement.
Cursor moves only if index finger is pointing up.
In addition to that cursor also moves if index and middle finger are up or index, middle and ring finger are up.
Clicking is performed by bending a thumb towards your hand.
There are 4 types of clicks which are differ by positions of other 4 fingers:

- single left click -- only index finger pointing up

- double left click -- index and middle finger pointing up

- right click -- index, middle and ring finger pointing up

- left toggle -- only index finger pointing up while thumb stays bent during the duration of a toggle
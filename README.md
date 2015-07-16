#rubyenv

This tool is inspired by [nodeenv](https://github.com/ekalinin/nodeenv) and allows you to install ruby into your virtualenvs.

Unlike nodeenv, rubyenv **only** works inside virtualenvs.

## Install

```
$ virtualenv myenv
$ source myenv/bin/activate
$ pip install rubyenv
$ rubyenv install 2.2.2
```

## Example

```
$ mkdir frontend
$ echo 'use_env frontend' > frontenv/.env
$ cd frontend
$ pip install nodeenv rubyenv
$ nodeenv -p --prebuilt
$ npm upgrade -g npm
$ node --version && npm --version
$ npm install -g yo bower grunt-cli generator-angular
$ rubyenv install 2.2.2
$ ruby --version && gem --version
$ gem install compass
$ yo angular
$ grunt serve
```

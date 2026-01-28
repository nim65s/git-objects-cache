# git objects-cache

A manual fetch cache for your git objects

> ⚠️ This is a footgun. If you don't like to shoot yourself in the feet, then don't use this footgun ⚠️

Therefore "this project destroyed 3 weeks of my work 😭" is not a valid issue. You've been warned.

## Usage

```
usage: git objects-cache [-h] [-q] [-v] [-f] {add,remove} ...

A manual fetch cache for your git objects

positional arguments:
  {add,remove}
    add          add (or update) a remote
    remove       remove a remote

options:
  -h, --help     show this help message and exit
  -q, --quiet    decrement verbosity level
  -v, --verbose  increment verbosity level
  -f, --fast     don't check/update remotes before fetching
```

## Config

(this file is created on first run if needed)

`~/.config/git-objects-cache/config.toml`, eg.:
```toml
[git-objects-cache]
repo = "~/.cache/git-objects-cache"

[remotes]
jrl-cmakemodules = "https://github.com/jrl-umi3218/jrl-cmakemodules"
example-robot-data = "https://github.com/gepetto/example-robot-data"
pinocchio = "https://github.com/stack-of-tasks/pinocchio"
rosdistro = "https://github.com/ros/rosdistro/"
```

## Idea

This create a big bare git repo just for cache.
In there, you can put one remote per project you want available in that cache, and `git fetch --all --no-tags --prune` as often as you want.

Then it create a init template with that repo in `objects/info/alternates`.

ℹ️ For that a `git config --global init.templateDir` will be run !

So next time you clone something, objects that are already fetched in that cache don't need to be downloaded again.

## Example

1. Install this, eg.

    `$ uv tool install git+https://github.com/nim65s/git-objects-cache`

2. `git` now has a `objects-cache` subcommand. It initialize its configuration and a cache on first run. In that first run you can already provide the url of a repo you want to cache:

    `$ git objects-cache -v add https://github.com/gepetto/example-robot-data`

    ```
    INFO:git-objects-cache:init...
    INFO:git-objects-cache:creating '~/.config/git-objects-cache' directory
    INFO:git-objects-cache:creating '~/.config/git-objects-cache/config.toml' file
    INFO:git-objects-cache:creating '~/.cache/git-objects-cache' repo
    Initialized empty Git repository in ~/.cache/git-objects-cache/
    INFO:git-objects-cache:creating '~/.config/git-objects-cache/template' template
    INFO:git-objects-cache:adding remote 'example-robot-data' to 'https://github.com/gepetto/example-robot-data'
    INFO:git-objects-cache:sync remotes with config file...
    INFO:git-objects-cache:adding 'example-robot-data' remote to 'https://github.com/gepetto/example-robot-data'
    INFO:git-objects-cache:updating cache...
    remote: Enumerating objects: 5241, done.
    remote: Counting objects: 100% (1274/1274), done.
    remote: Compressing objects: 100% (307/307), done.
    remote: Total 5241 (delta 1103), reused 968 (delta 967), pack-reused 3967 (from 3)
    Receiving objects: 100% (5241/5241), 196.75 MiB | 14.79 MiB/s, done.
    Resolving deltas: 100% (2393/2393), done.
    From https://github.com/gepetto/example-robot-data
     * [new branch]      devel                    -> example-robot-data/devel
     * [new branch]      master                   -> example-robot-data/master
     * [new branch]      update_flake_lock_action -> example-robot-data/update_flake_lock_action
    ```

3. Your next `git clone` of that repo is basically free 🎉 (compare the numbers in the `Receiving objects` lines):

    `$ git clone https://github.com/gepetto/example-robot-data`

    ```
    Cloning into 'example-robot-data'...
    remote: Enumerating objects: 43, done.
    remote: Total 43 (delta 0), reused 0 (delta 0), pack-reused 43 (from 2)
    Receiving objects: 100% (43/43), 32.81 KiB | 1.17 MiB/s, done.
    Updating files: 100% (1084/1084), done.
    ```

4. Maintain your `~/.config/git-objects-cache/config.toml` as you want (`$EDITOR` or `git objects-cache {add,delete}`), and fetch updates to your cache when you want (`git objects-cache`)


## Why

In cases you want to cache, because eg.

- some tools just want to `git clone` again and again same stuff
- dozens of projects have the same submodule

If you believe those are wrong problems, yes, this is known, thanks.

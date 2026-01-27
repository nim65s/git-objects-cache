# git objects cache

A big fetch cache for your git objects

> ⚠️ This is a footgun. If you don't like to shoot yourself in the feet, then don't use this footgun ⚠️

Therefore "this project destroyed 3 weeks of my work" is not a valid issue. You've been warned.

## Config

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

(this file is created on first run if needed)

## Idea

This create a big bare git repo just for cache.
In there, you can put one remote per project you want available in that cache, and `git fetch --all --no-tags --prune` as often as you want.

Then it create a init template with that repo in objects/info/alternates.

So next time you clone something, objects that are already fetched in that cache don't need to be downloaded again.

## Why

In cases you want to cache, because eg.

- some tools just want to `git clone` again and again same stuff
- dozens of projects have the same submodule

If you believe those are wrong problems, yes, this is known, thanks.

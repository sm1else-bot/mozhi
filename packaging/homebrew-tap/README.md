# Official Mozhi Homebrew tap

The public maintainer tap lives at <https://github.com/sm1else-bot/homebrew-mozhi>.
It is separate from Homebrew/core.

```sh
brew install sm1else-bot/mozhi/mozhi
brew test sm1else-bot/mozhi/mozhi
brew update
brew upgrade mozhi
brew uninstall mozhi
```

The tap supports macOS ARM64/Intel and Linux x64 using verified native release
archives with Python bundled. Its CI installs, tests, reinstalls and uninstalls
through real public release URLs on all three native runners.

For future releases, the complete language build generates
`dist/package-managers/homebrew-mozhi/Formula/mozhi.rb` with actual archive hashes.
Publish the approved immutable GitHub Release assets, verify every public URL,
then update the tap with that generated formula and release evidence. Require
its native CI to pass and test upgrades from the preceding version. The tap's
README contains the full maintainer procedure.

For short-name `brew install mozhi` on Homebrew 6, tap first, then run
`brew trust --formula sm1else-bot/mozhi/mozhi`. Fully qualified installation
already selects and trusts only this formula.

Homebrew/core acceptance would require a separate eligible source-based formula
and review; this tap does not claim that acceptance.

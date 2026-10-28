# Prepared official tap: sm1else-bot/homebrew-mozhi

The complete native build creates `dist/package-managers/homebrew-mozhi/Formula/mozhi.rb`
using actual macOS ARM64/x64 and Linux x64 artifact hashes. This directory does
not contain a placeholder formula with invented checksums.

After an explicitly approved release is public, create the public repository
`sm1else-bot/homebrew-mozhi`, copy the generated `Formula/mozhi.rb` and a README
there, run its tests, then publish the tap. Consumers can then use:

```
brew tap sm1else-bot/mozhi
brew install sm1else-bot/mozhi/mozhi
brew test mozhi
brew upgrade mozhi
brew uninstall mozhi
```

Those are post-publication commands, not a claim that the tap exists today.
For the unqualified `brew install mozhi` command on Homebrew 6, first run
`brew trust --formula sm1else-bot/mozhi/mozhi`. Tapping alone does not grant
formula trust. This is separate from Homebrew/core acceptance.
Homebrew/core normally requires source builds, suitable licensing, maintained
upstream releases, and formula review. Submit a source-based core formula through
Homebrew's contribution process once eligible; an upstream binary tap formula is
not automatically suitable for core.

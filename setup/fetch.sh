#!/bin/bash
# Clone each method's upstream code at the tested commit and apply its patch.
#   bash setup/fetch.sh sgf longlive          # or: bash setup/fetch.sh all
# Code goes to third_party/<method>; weights are not downloaded.
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
ALL="sgf sgf_plus recency_forcing longlive context_forcing rolling_sink id_forcing tethercache"

upstream() {   # prints "<git url> <commit>"
  case $1 in
    sgf)             echo https://github.com/zhuang2002/Self_Gradient_Forcing.git ba16e1b70d537b2b9f542efc9c6ef4cef1819d8c ;;
    sgf_plus)        echo https://github.com/Zihan-Su/Self_Gradient_Forcing_Plus.git 14cda9bb35f87000fbc11138a5170002d213effe ;;
    recency_forcing) echo https://github.com/guandeh17/Self-Forcing.git 33593df3e81fa3ec10239271dd2c100facac6de1 ;;
    longlive)        echo https://github.com/NVlabs/LongLive.git e52d9ef6865d843282a6b5e9d46d03b35f88929d ;;
    context_forcing) echo https://github.com/chenshuo20/Context-Forcing.git 9ba918d6009f4d9a773258c510c5d792630b4718 ;;
    rolling_sink)    echo https://github.com/Rolling-Sink/Rolling-Sink.git e384dc7c08e8848b03df29968b34574bbf96fc3b ;;
    tethercache)     echo https://github.com/my4f175/TetherCache.git 37c581ace23ff5df201f45e8282065d19b4ace8c ;;
    id_forcing)      echo https://github.com/In-Distribution-Forcing/ID-Forcing.git 4cd6a4c572ba6a9725a08ff590f9661ad2ea3cb2 ;;
    *) echo "unknown method: $1 (choose from: $ALL)" >&2; return 1 ;;
  esac
}

[ $# -eq 0 ] || [ "$1" = all ] && set -- $ALL
for m in "$@"; do
  info=$(upstream "$m")
  read -r url commit <<< "$info"
  d=$ROOT/third_party/$m
  [ -d "$d/.git" ] || git clone "$url" "$d"
  git -C "$d" checkout --quiet "$commit"
  p=$ROOT/integrations/$m/commit_rule.patch
  if [ ! -f "$p" ]; then
    echo "$m: at ${commit:0:7} (no patch: generate.py imports the upstream code as is)"
  elif git -C "$d" apply --check "$p" 2>/dev/null; then
    git -C "$d" apply "$p" && echo "$m: patched at ${commit:0:7}"
  elif git -C "$d" apply --check --reverse "$p" 2>/dev/null; then
    echo "$m: patch already applied"
  else
    echo "$m: the patch does not apply; is third_party/$m at ${commit:0:7} without local changes?" >&2; exit 1
  fi
done

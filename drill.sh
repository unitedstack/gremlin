#!/bin/bash

# With LANG set to everything else than C completely undercipherable errors
# like "file not found" and decoding errors will start to appear during scripts
# or even ansible modules
LANG=C

GREM_DIR=$(dirname $( readlink -f "${BASH_SOURCE[0]}" ))
DEFAULT_OPT_TAGS="untagged"


: ${OPT_TAGS:=$DEFAULT_OPT_TAGS}
: ${OPT_PLAYBOOK:=$GREM_DIR/playbooks/drill.yml}
: ${OPT_WORKDIR:=$GREM_DIR/.gremlin}
: ${OPT_CONFIG:=$GREM_DIR/config.yml}


usage () {
    echo "Usage: $0 [options]"
    echo ""
    echo "Basic options:"
    echo "  -p, --playbook <file>"
    echo "                      playbook to run(default=$OPT_PLAYBOOK)"
    echo "  -c, --config <file>"
    echo "                      specify the config file that contains the node"
    echo "                      configuration, can be used only once"
    echo "                      (default=$OPT_CONFIG)"
    echo ""
    echo "Advanced options:"
    echo "  -v, --ansible-debug"
    echo "                      invoke ansible-playbook with -vvvv"
    echo "  -t, --tags <tag1>[,<tag2>,...]"
    echo "                      only run plays and tasks tagged with these values,"
    echo "                      specify 'all' to run everything"
    echo "                      (default=$OPT_TAGS)"
    echo "  -S, --skip-tags <tag1>[,<tag2>,...]"
    echo "                      only run plays and tasks whose tags do"
    echo "                      not match these values"
    echo "  -w, --working-dir <dir>"
    echo "                      directory where the inventory, config files, etc."
    echo "                      are created (default=$OPT_WORKDIR)"
    echo "  -h, --help          print this help and exit"
}


while [ "x$1" != "x" ]; do
    case "$1" in
        --ansible-debug|-v)
            OPT_DEBUG_ANSIBLE=1
            ;;
        --config|-c)
            OPT_CONFIG=$2
            shift
            ;;
        --tags|-t)
            OPT_TAGS=$2
            shift
            ;;
        --skip-tags|-S)
            OPT_SKIP_TAGS=$2
            shift
            ;;
        --working-dir|-w)
            OPT_WORKDIR=$(realpath $2)
            shift
            ;;
        --help|-h)
            usage
            exit
            ;;
        --)
            shift
            break
            ;;
        *)
            break
            ;;
    esac
    shift
done


if [ "$#" -lt 1 ]; then
    echo "ERROR: You must specify a playbook." >&2
    usage >&2
    exit 2
fi

if [ "$#" -gt 2 ]; then
    usage >&2
    exit 2
fi


set -ex

export ANSIBLE_CONFIG=$GREM_DIR/ansible.cfg
export ANSIBLE_INVENTORY=$GREM_DIR/inventory/hosts

if [ "$OPT_DEBUG_ANSIBLE" = 1 ]; then
    VERBOSITY=vvvv
else
    VERBOSITY=vv
fi

ansible-playbook -$VERBOSITY $OPT_PLAYBOOK \
    -e @$OPT_CONFIG \
    ${OPT_TAGS:+-t $OPT_TAGS} \
    ${OPT_SKIP_TAGS:+--skip-tags $OPT_SKIP_TAGS}

set +x

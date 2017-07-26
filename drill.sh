#!/bin/bash

# With LANG set to everything else than C completely undercipherable errors
# like "file not found" and decoding errors will start to appear during scripts
# or even ansible modules
LANG=C

GREM_DIR=$(dirname $( readlink -f "${BASH_SOURCE[0]}" ))
DEFAULT_OPT_TAGS="untagged,verification,fault"


: ${OPT_TAGS:=$DEFAULT_OPT_TAGS}
: ${OPT_PLAYBOOK:=$GREM_DIR/playbooks/drill.yml}
: ${OPT_WORKDIR:=$GREM_DIR/.gremlin}
: ${OPT_CONFIG:=$GREM_DIR/config.yml}


install_deps () {
    sudo yum -y install epel-release
    sudo yum clean all
    sudo yum makecache
    sudo yum -y install ansible git
}

usage () {
    echo "Usage: $0 --install-deps"
    echo "                      install quickstart package dependencies and exit"
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Basic options:"
    echo "  -p, --playbook <file>"
    echo "                      playbook to run(default=$OPT_PLAYBOOK)"
    echo "  -i, --inventory <file>"
    echo "                      specify inventory host path"
    echo "                      (default=/etc/ansible/hosts) or comma separated host list"
    echo "  -c, --config <file>"
    echo "                      specify the config file that contains the node"
    echo "                      configuration, can be used only once"
    echo "                      (default=$OPT_CONFIG)"
    echo "  -s, --step"
    echo "                      Execute playbooks or tasks step by step"
    echo "  --syntax-check"
    echo "                      perform a syntax check on the playbook, but do not"
    echo "                      execute it"
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

OPT_VARS=()

while [ "x$1" != "x" ]; do
    case "$1" in
        --install-deps)
            OPT_INSTALL_DEPS=1
            ;;
        --inventory|-i)
            OPT_INVENTORY=$2
            shift
            ;;
        --playbook|-p)
            OPT_PLAYBOOK=$2
            shift
            ;;
        --extra-vars|-e)
            OPT_VARS+=("-e")
            OPT_VARS+=("$2")
            shift
            ;;
        --config|-c)
            OPT_CONFIG=$2
            shift
            ;;
        --step|-s)
            OPT_STEP=1
            ;;
        --syntax-check)
            OPT_SYNTAX_CHECK=1
            ;;
        --ansible-debug|-v)
            OPT_DEBUG_ANSIBLE=1
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


if [ "$OPT_INSTALL_DEPS" = 1 ]; then
    echo "NOTICE: installing dependencies"
    install_deps
    exit $?
fi


if [ "$#" -gt 2 ]; then
    usage >&2
    exit 2
fi


set -ex

export ANSIBLE_CONFIG=$GREM_DIR/ansible.cfg
#export ANSIBLE_INVENTORY=$GREM_DIR/inventory/hosts

if [ "$OPT_DEBUG_ANSIBLE" = 1 ]; then
    VERBOSITY=vvvv
else
    VERBOSITY=vv
fi

ansible-playbook -$VERBOSITY $OPT_PLAYBOOK \
    -e @$OPT_CONFIG \
    -e local_working_dir=$OPT_WORKDIR \
    ${OPT_VARS[@]} \
    ${OPT_INVENTORY:+-i $OPT_INVENTORY} \
    ${OPT_TAGS:+-t $OPT_TAGS} \
    ${OPT_SKIP_TAGS:+--skip-tags $OPT_SKIP_TAGS} \
    ${OPT_STEP:+--step} \
    ${OPT_SYNTAX_CHECK:+--syntax-check}

set +x

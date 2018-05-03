# setup server
ansible-playbook -s ubuntu_base.yml

# restart elasticsearch
ansible-playbook -s elasticsearch.yml

# restart supervisor
ansible-playbook -s supervisor.yml

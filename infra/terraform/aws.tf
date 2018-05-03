provider "aws" {
  # credentials are stored in ~/.aws/credentials
  region     = "us-west-1"
}

resource "aws_ebs_volume" "elasticsearch001" {
  availability_zone = "us-west-1c"
  size              = 30
  type = "gp2"
}

resource "aws_instance" "arb_app_001" {
  availability_zone = "us-west-1c"
//  ami             = "ami-09d2fb69" # Ubuntu Server 16.04 LTS (HVM), SSD Volume Type
  ami             = "ami-b2527ad2" # Ubuntu, 14.04 LTS
  instance_type   = "t2.micro"
  key_name        = "arb_jin"
  security_groups = ["arb001__internal"]
  root_block_device = {
    volume_size = 10
    volume_type = "gp2"
  }
  tags {
    Name = "app_001"
  }
}

resource "aws_instance" "arb_data_001" {
  availability_zone = "us-west-1c"
//  ami             = "ami-09d2fb69" # Ubuntu Server 16.04 LTS (HVM), SSD Volume Type
  ami             = "ami-b2527ad2" # Ubuntu, 14.04 LTS
  instance_type   = "t2.small"
  key_name        = "arb_jin"
  security_groups = ["arb001__internal"]
  root_block_device = {
    volume_size = 10
    volume_type = "gp2"
  }

  tags {
    Name = "elasticsearch__001"
  }
}

//resource "aws_instance" "arb_data_002" {
//  availability_zone = "us-west-1c"
//  //  ami             = "ami-09d2fb69" # Ubuntu Server 16.04 LTS (HVM), SSD Volume Type
//  ami             = "ami-b2527ad2" # Ubuntu, 14.04 LTS
//  instance_type   = "t2.small"
//  key_name        = "arb_jin"
//  security_groups = ["arb001__internal"]
//  root_block_device = {
//    volume_size = 10
//    volume_type = "gp2"
//  }
//
//  tags {
//    Name = "elasticsearch__001"
//  }
//}


resource "aws_volume_attachment" "attachment_elaticsearch001" {
  device_name = "/dev/xvdh"
  volume_id   = "${aws_ebs_volume.elasticsearch001.id}"
  instance_id = "${aws_instance.arb_data_001.id}"
  force_detach = false
}

output "arb_app__001" {
  value = "${aws_instance.arb_app_001.public_ip}"
}

output "arb_data__001" {
  value = "${aws_instance.arb_data_001.public_ip}"
}

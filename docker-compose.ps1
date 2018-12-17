param ( [string]$target="run" )

# Set-ExecutionPolicy Unrestricted -Scope CurrentUser

$global:PYTHON_VERSION="3.7"


if ($target -eq "install" ) {

}

if ($target -eq "run") {
    # dev local mount
    docker-compose --file docker-compose.yml --file processmedia2/docker-compose.yml up
}

<#
.SYNOPSIS
    PowerShell script to build and optionally push Docker images based on provided names and configurations.

.DESCRIPTION
    This script automates the process of building Docker images from specified source directories. 
    It handles special cases for certain image names and allows the use of build arguments such as `MODE` for `client` builds.
    
    The script also manages Docker repositories by saving the last used repository to a file (`.repository`). 
    If the `push` option is specified, and a repository is not provided or saved, an error will be thrown.

.PARAMETER images
    A comma-separated list of image names to build. The script determines the appropriate Dockerfile and context path 
    based on the name format. If the name contains a slash (e.g., `backend/api`), the Dockerfile path is derived accordingly. 
    If no slash is present, it looks for a Dockerfile in the corresponding directory (e.g., `../src/playground/Dockerfile`).

.PARAMETER repository
    The Docker repository to use for tagging the images. If provided, this repository is saved for future use.
    If not provided but previously saved, the saved repository will be used. If `push` is specified and no repository 
    is provided or saved, the script will throw an error.

.PARAMETER push
    A switch parameter that, when specified, will push the built Docker images to the repository. 
    Requires a repository to be provided or previously saved.

.EXAMPLE
    .\build_images.ps1 -images "client,backend/api" -repository "mydockerhub"

    This command builds the `client` and `backend/api` images, tagging them with the repository `mydockerhub`. 
    The repository `mydockerhub` is saved for future use.

.EXAMPLE
    .\build_images.ps1 -images "playground,backend/api" -push

    This command builds the `playground` and `backend/api` images, using the saved repository for tagging, 
    and pushes the images to the repository.

.EXAMPLE
    .\build_images.ps1 -images "client:local,playground/environment:ubuntu" -repository "mydockerhub" -push

    This command builds the `client` image with `MODE=local` and the `playground/environment` image using the 
    `ubuntu` Dockerfile. It tags the images with the repository `mydockerhub` and pushes them to the repository.

.NOTES
    The script logs detailed information about the build process, including paths checked for Dockerfiles and 
    any errors encountered. Logs are saved to `build_images.log`.
#>

param(
    [string]$images,
    [string]$repository,
    [switch]$push
)

# Log file path
$logFilePath = "build_images.log"

# Repository file path
$repositoryFilePath = ".repository"

# Function to log messages
function Write-Log {
    param(
        [string]$message,
        [string]$type = "INFO"
    )

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] [$type] $message"
    Write-Host $logMessage
    Add-Content -Path $logFilePath -Value $logMessage
}

# Validate input
if (-not $images) {
    Write-Log "The 'images' argument is required." "ERROR"
    exit 1
}

# Handle repository saving and loading
if ($repository) {
    Write-Log "Saving repository '$repository' to $repositoryFilePath"
    Set-Content -Path $repositoryFilePath -Value $repository
}
elseif (-not $repository -and (Test-Path $repositoryFilePath)) {
    $repository = (Get-Content -Path $repositoryFilePath -Raw).Trim()
    Write-Log "Using saved repository '$repository' from $repositoryFilePath"
}

# Check if repository is required for push
if ($push -and -not $repository) {
    Write-Log "The 'repository' argument is required when 'push' is specified and no saved repository is found." "ERROR"
    exit 1
}

# Start logging
Write-Log "Build process started with arguments: images='$images', repository='$repository', push='$push'"

# Define the name to image tag map
$nameToTagMap = @{
    "backend/api"            = "api"
    "backend/database"       = "postgres"
    "playground"             = "playground-controller"
    "playground/controller"  = "playground-controller"
    "playground/environment" = "playground-environment"
    "client"                 = "app"
}

# Split the images argument into individual names
$imageNames = $images -split ','

# Initialize an array to store the built tag names
$builtTags = @()

# Process each image name
foreach ($name in $imageNames) {
    $name = $name.Trim()
    Write-Log "Processing image name: $name"

    $suffix = ""
    $buildArgs = ""

    if ($name -match ":") {
        $parts = $name -split ':'
        $name = $parts[0]
        $suffix = "-$($parts[1].Trim())"
        Write-Log "Detected suffix '$suffix' for image name '$name'"
    }

    $contextPath = ""
    $dockerfilePath = ""

    try {
        # Handle special case for client with MODE build arg
        if ($name -eq "client") {
            $mode = $suffix.TrimStart('-')
            if (-not $mode) {
                $mode = "prod"
            }
            $contextPath = "../src/client"
            $dockerfilePath = "$contextPath/Dockerfile"
            $buildArgs = "--build-arg MODE=$mode"
            Write-Log "Client build with MODE '$mode'. Using context path '$contextPath' and Dockerfile '$dockerfilePath'"
        }
        # Handle special case for playground/environment with suffix
        elseif ($name -eq "playground/environment") {
            $dockerfilePath = "../src/playground/environments/$($suffix.TrimStart('-')).Dockerfile"
            if (-not (Test-Path $dockerfilePath)) {
                Write-Log "Specific Dockerfile not found at '$dockerfilePath', falling back to default Dockerfile"
                $dockerfilePath = "../src/playground/environment.Dockerfile"
            }
            $contextPath = "../src/playground"
            Write-Log "Using context path '$contextPath' and Dockerfile '$dockerfilePath' for '$name'"
        }
        # Handle cases where the name contains a slash (like backend/api)
        elseif ($name -match "/") {
            $baseName = $name.Split('/')[-1]
            $contextPath = "../src/$($name.Substring(0, $name.LastIndexOf('/')))"
            $dockerfilePath = "$contextPath/$baseName.Dockerfile"
            Write-Log "Checking Dockerfile at '$dockerfilePath' for '$name'"

            if (-not (Test-Path $dockerfilePath)) {
                throw "Dockerfile for '$name' not found at expected location '$dockerfilePath'."
            }
        }
        # Handle job case in ../src/backend/jobs
        elseif (Test-Path "../src/backend/jobs/$name") {
            $contextPath = "../src/backend"
            $dockerfilePath = "../src/backend/jobs/Dockerfile"
            $buildArgs = "--build-arg JOB_NAME=$name"
            Write-Log "Detected job: '$name'. Using context path '$contextPath' and Dockerfile '$dockerfilePath'"
        }
        else {
            # Handle cases where the name does not contain a slash (like playground)
            $contextPath = "../src/$name"
            $dockerfilePath = "$contextPath/Dockerfile"
            Write-Log "Checking Dockerfile at '$dockerfilePath' for '$name'"

            if (-not (Test-Path $dockerfilePath)) {
                throw "Dockerfile for '$name' not found at expected location '$dockerfilePath'."
            }
        }

        # Determine the image tag
        if ($nameToTagMap.ContainsKey($name)) {
            $imageTag = $nameToTagMap[$name] + $suffix
        }
        else {
            $imageTag = $name + $suffix
        }

        # Add repository prefix if provided
        if ($repository) {
            $fullTag = "$repository/$imageTag"
        }
        else {
            $fullTag = $imageTag
        }

        # Build the Docker image
        Write-Log "Building image '$fullTag' from '$dockerfilePath' with context '$contextPath'..."
        $buildCommand = "docker build -t $fullTag -f $dockerfilePath $contextPath $buildArgs"
        Invoke-Expression $buildCommand

        if ($push) {
            # Push the Docker image
            Write-Log "Pushing image '$fullTag' to repository..."
            $pushCommand = "docker push $fullTag"
            Invoke-Expression $pushCommand
        }

        # Add the built tag to the list
        $builtTags += $fullTag
        Write-Log "Successfully built and processed '$fullTag'"
    }
    catch {
        Write-Log "Error processing '$name': $_" "ERROR"
        exit 1
    }
}

# Output the built tags
Write-Log "Build process completed. Built tags:"
$builtTags | ForEach-Object { 
    Write-Log $_
    Write-Host $_ 
}

# BingeSuggest-next

[![DOI](https://zenodo.org/badge/945669213.svg)](https://doi.org/10.5281/zenodo.15220784)

<a href="https://img.shields.io/badge/python-v3.12.2-yellow.svg" alt="Python version">
<img src="https://img.shields.io/badge/python-v3.12.2-yellow.svg"/> </a>

<!-- Release Badge -->
<a href="https://img.shields.io/github/release/CSC510-Group18/BingeSuggest-next?color=brightblue" alt="Release">
<img src="https://img.shields.io/github/release/CSC510-Group18/BingeSuggest-next?color=brightblue"/> </a>

<a href="https://github.com/CSC510-Group18/BingeSuggest-next/blob/master/LICENSE">
<img src="https://img.shields.io/github/license/CSC510-Group18/BingeSuggest-next?style=plastic"></a>


BingeSuggest-next is a modern movie suggestion and review web application. This project is a complete rewrite by Teddy (tddschn) from the previous 1990-style jQuery/Flask version, incorporating modern React / Next.js and TypeScript practices with a rich UI. We have extended the application to be faster, more user friendly, and easier to develop for future engineers.

Prevous version: https://github.com/CSC510-Group13/BingeSuggest

- [BingeSuggest-next](#bingesuggest-next)
  - [Demo](#demo)
  - [Features](#features)
  - [Improvements over the previous version](#improvements-over-the-previous-version)
  - [Running the Backend](#running-the-backend)
  - [Running the Frontend](#running-the-frontend)
    - [Installation](#installation)
    - [Running in Development](#running-in-development)
    - [Building](#building)
    - [Deploying](#deploying)
    - [Web App Dir Structure](#web-app-dir-structure)
  - [Cite this Project](#cite-this-project)
  - [License](#license)


## Demo

[Demo Video](https://drive.google.com/file/d/18EnE-xooV2McsirnXATbysHrqtNRHbj8/view?usp=sharing)


Click on the link to view the demo video. The video showcases the new features and improvements in BingeSuggest-next, including the UI improvements, performance enhancements, and additional functionalities.

## Features

- **User Authentication:** Users can log in, create accounts, or continue as a guest. See [artifact-component.tsx](#file:artifact-component.tsx-context) for the login component.
- **Movie Search:** Real-time movie search powered by a dropdown that shows suggestions. Check out [MovieSearchDropdown.tsx](#file:MovieSearchDropdown.tsx-context) for details.
- **Watchlist & Watched History:** Users can manage their watchlist and mark movies as watched.
- **Reviews and Discussion:** Posting comments and reviews for movies, viewing recent reviews in a streamlined UI.
- **Friend Activity:** Social feature to add and monitor friend activity.
- **Recommendations:** Personalized movie recommendations based on genre, director, or actor.

## Improvements over the previous version

- Performance: Cache work from the first recommendation of a session to make future recommendations take significantly less time.
- Thumbnails: Search tab and display genie now displays thumbnails so users can be more sure of the movie they are looking up.
- Database migration: Moving from MySQL to sqlite3 will make it easier for future developers to work on this application with increase velocity.
- Various Bug Fixes

## Running the Backend

```
cd backend/src/recommenderapp && python3 app.py
```

## Running the Frontend

- [Node.js](https://nodejs.org/) installed
- [Bun](https://bun.sh) for fast development and build times
- [Vite](https://vitejs.dev/) for development server and bundling

### Installation

1. Clone the repository and cd into `frontend`
2. Install dependencies with:
   ```sh
   bun install
   ```

### Running in Development

Start the development server with:
```sh
bun run dev
```

### Building

Build the production version with Vite and TypeScript using:
```sh
bun run build
```

Alternatively, to build a single file, use the Makefile target:
```sh
make build-single-file
```
This target installs dependencies, runs Vite build, and outputs the built file as specified in Makefile.

### Deploying

After building, you can deploy the output file. There is also a Makefile target to publish the build to a gist:
```sh
make publish-to-gist
```
This command creates a gist (with modifications) for easy sharing and deployment.

### Web App Dir Structure

- **src/artifact-component.tsx:** Main application component including major features such as login, search, watchlist, and reviews.
- **src/components/MovieSearchDropdown.tsx:** A reusable movie search dropdown component that uses real-time search via API.
- **Makefile:** Provides commands for building and deploying (refer to the Makefile for more details).

## Cite this Project

```bibtex
@software{BingeSuggest-next,
  author = {Jakub Jon and Jeff Powell and Zeiad Yakout},
  title = {BingeSuggest-next},
  year = {2025},
  url = {https://github.com/CSC510-Group18/BingeSuggest},
  note = {A modern movie suggestion and review web application.}
}
```

## License

MIT

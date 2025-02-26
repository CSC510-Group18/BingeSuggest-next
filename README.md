# BingeSuggest-next

BingeSuggest-next is a modern movie suggestion and review web application. This project is a complete rewrite by Teddy (tddschn) from the previous 1990-style jQuery/Flask version, incorporating modern React / Next.js and TypeScript practices with a rich UI.

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


<!-- <iframe src="https://drive.google.com/file/d/1-dDDALwgS7VVANqMezGMK5_OEquLFFK5/preview" width="640" height="480" allow="autoplay"></iframe> -->

We also compared this version to prevous version of BingeSuggest. The new version is a complete rewrite using modern technologies and practices, resulting in a more efficient and user-friendly application.

[![](https://cdn.discordapp.com/attachments/1332562207741055056/1344138393403133994/CleanShot-2025-02-25-21.45.59.png?ex=67bfd1ed&is=67be806d&hm=33944122ee61a337020f84dd6f57201c93379c1ffb491a6f0a919e2089f620d5&)](https://drive.google.com/file/d/1-dDDALwgS7VVANqMezGMK5_OEquLFFK5/view?usp=sharing)

Click on the image to view the demo video. The video showcases the new features and improvements in BingeSuggest-next, including the new UI, performance enhancements, and additional functionalities.

## Features

- **User Authentication:** Users can log in, create accounts, or continue as a guest. See [artifact-component.tsx](#file:artifact-component.tsx-context) for the login component.
- **Movie Search:** Real-time movie search powered by a dropdown that shows suggestions. Check out [MovieSearchDropdown.tsx](#file:MovieSearchDropdown.tsx-context) for details.
- **Watchlist & Watched History:** Users can manage their watchlist and mark movies as watched.
- **Reviews and Discussion:** Posting comments and reviews for movies, viewing recent reviews in a streamlined UI.
- **Friend Activity:** Social feature to add and monitor friend activity.
- **Recommendations:** Personalized movie recommendations based on genre, director, or actor.

## Improvements over the previous version

- Performance: Converted code to now a Single Page Application (SPA), utilizing client-side navigation that allows users to navigate to different part of the app at the speed of light. A significant performance increase of over 1000x on some pages!
- Friends: Users can now add friends and browse their watch history.
- Movie Search: New and intuitive "Search" tab that expands off the previous iterations "Recommendations" tab. Search movies fast with this new feature!
- Recommendation: Users now have access to AI-powered movie recommendation assistance through our Recommendation Genie.
- UI Enhancements: Frontend rewritten from scratch featuring a new modern UI design. Migrated from jQuery to React, Bun, TypeScript, Tailwind, and many other newer technologies. Intuitive interface and layout!
- Dark Mode: Users now have access to a dark mode toggle at the top right.
- Guest Users: It is now clear to guest users their approved features. Features they cannot access have restrictions. Different views for guests and users. No more error messages as a guest!
- Various Bug Fixes

## Running the Backend

Using gunicorn instead of vanilla Flask for better performance and scalability.

```
cd backend/src/recommenderapp && gunicorn app:app -b localhost:5000
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
  author = {Ryan Mikula and Teddy Chen and Mulikatu Yakubu},
  title = {BingeSuggest-next},
  year = {2025},
  url = {https://github.com/CSC510-Group13/BingeSuggest},
  note = {A modern movie suggestion and review web application.}
}
```

## License

MIT

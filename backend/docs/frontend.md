# BingeSuggest-next frontend

BingeSuggest-next is a modern movie suggestion and review web application. This project is a complete rewrite by Teddy (tddschn) from the previous 1990-style jQuery/Flask version, incorporating modern React / Next.js and TypeScript practices with a rich UI.

Prevous version: https://github.com/CSC510-Group13/BingeSuggest

## Demo



https://github.com/user-attachments/assets/7e24871a-9afb-4ef0-904c-d05a0ca8791c



## Features

- **User Authentication:** Users can log in, create accounts, or continue as a guest. See [artifact-component.tsx](#file:artifact-component.tsx-context) for the login component.
- **Movie Search:** Real-time movie search powered by a dropdown that shows suggestions. Check out [MovieSearchDropdown.tsx](#file:MovieSearchDropdown.tsx-context) for details.
- **Watchlist & Watched History:** Users can manage their watchlist and mark movies as watched.
- **Reviews and Discussion:** Posting comments and reviews for movies, viewing recent reviews in a streamlined UI.
- **Friend Activity:** Social feature to add and monitor friend activity.
- **Recommendations:** Personalized movie recommendations based on genre, director, or actor.

## Improvements over the previous version

- Performance: Frontend rewritten from scratch, now a Single Page Application (SPA), utilizing client-side navigation to allow users to navigate to different part of the app at the speed of light.

## Getting Started

### Prerequisites

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

## Project Structure

- **src/artifact-component.tsx:** Main application component including major features such as login, search, watchlist, and reviews.
- **src/components/MovieSearchDropdown.tsx:** A reusable movie search dropdown component that uses real-time search via API.
- **Makefile:** Provides commands for building and deploying (refer to the Makefile for more details).

## Credits

This project is a complete rewrite by Teddy (tddschn), modernizing the original 1990-style jQuery/Flask version into a robust React-based application.

## License

MIT

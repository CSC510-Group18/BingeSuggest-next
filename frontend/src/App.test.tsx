import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import App from "./artifact-component"; // Updated import with extension
import "@testing-library/jest-dom/extend-expect";
// import jest, beforeEach, afterEach from "jest";
import { beforeEach, afterEach, describe } from "@jest/globals";
import { test, expect, jest } from "@jest/globals";

// A helper to mock the global fetch
const mockFetch = (data: any, ok = true) =>
  Promise.resolve({
    ok,
    json: () => Promise.resolve(data),
  } as Response);

beforeEach(() => {
  jest.spyOn(global, "fetch").mockImplementation(() => {
    return mockFetch({});
  });
});

afterEach(() => {
  jest.restoreAllMocks();
  // Reset dark mode state in document
  document.documentElement.classList.remove("dark");
});

describe("App Component", () => {
  test("renders header and login tab when not logged in", () => {
    render(<App />);
    expect(screen.getByText("BingeSuggest")).toBeInTheDocument();
    // When user is null, login tab should be rendered
    expect(screen.getByText("Login")).toBeInTheDocument();
  });

  test("handles login success", async () => {
    // Mock a successful login response
    (global.fetch as jest.Mock).mockImplementationOnce(() =>
      mockFetch({}, true)
    );
    render(<App />);
    // Type username and password into inputs
    fireEvent.change(screen.getByPlaceholderText(/username/i), {
      target: { value: "testuser" },
    });
    fireEvent.change(screen.getByPlaceholderText(/password/i), {
      target: { value: "secret" },
    });
    // Click login button
    fireEvent.click(screen.getByText("Login"));
    // Since our mock is success, wait for UI update (user state changes)
    await waitFor(() => {
      // Tabs for logged in user should appear (e.g. Watchlist)
      expect(screen.getByText("Watchlist")).toBeInTheDocument();
    });
  });

  test("handles login failure", async () => {
    // Force login failure (non-ok response)
    (global.fetch as jest.Mock).mockImplementationOnce(() =>
      Promise.resolve({
        ok: false,
        json: () => Promise.resolve({}),
      })
    );
    render(<App />);
    fireEvent.change(screen.getByPlaceholderText(/username/i), {
      target: { value: "wronguser" },
    });
    fireEvent.change(screen.getByPlaceholderText(/password/i), {
      target: { value: "wrongpass" },
    });
    fireEvent.click(screen.getByText("Login"));
    await waitFor(() =>
      expect(
        screen.getByText("Login failed. Check your username and password.")
      ).toBeInTheDocument()
    );
  });

  test("handles login network error", async () => {
    // Force a network error during login
    (global.fetch as jest.Mock).mockImplementationOnce(() =>
      Promise.reject(new Error("Network error"))
    );
    render(<App />);
    fireEvent.change(screen.getByPlaceholderText(/username/i), {
      target: { value: "netuser" },
    });
    fireEvent.change(screen.getByPlaceholderText(/password/i), {
      target: { value: "netfail" },
    });
    fireEvent.click(screen.getByText("Login"));
    await waitFor(() =>
      expect(
        screen.getByText("An error occurred during login.")
      ).toBeInTheDocument()
    );
  });

  test("toggles between Login and Create Account modes", () => {
    render(<App />);
    // Initially in login mode
    expect(screen.getByText("Login")).toBeInTheDocument();
    // Click switch button
    fireEvent.click(screen.getByText("Create Account"));
    expect(screen.getByText("Create Account")).toBeInTheDocument();
  });

  test("SearchPage updates dropdown on input", async () => {
    // Provide a mock response for search API
    (global.fetch as jest.Mock).mockImplementationOnce(() =>
      mockFetch(["Movie A (tt123)", "Movie B (tt456)"])
    );
    render(<App />);
    // Navigate to Search tab
    fireEvent.click(screen.getByText("Search"));
    const input = screen.getByPlaceholderText("Search for movies...");
    fireEvent.change(input, { target: { value: "Mov" } });
    await waitFor(() => {
      expect(screen.getByText("Movie A (tt123)")).toBeInTheDocument();
      expect(screen.getByText("Movie B (tt456)")).toBeInTheDocument();
    });
  });

  test("SearchPage does not search for short queries", async () => {
    render(<App />);
    fireEvent.click(screen.getByText("Search"));
    const input = screen.getByPlaceholderText("Search for movies...");
    fireEvent.change(input, { target: { value: "Mo" } });
    await waitFor(() => {
      // Dropdown should not appear
      expect(screen.queryByRole("list")).not.toBeInTheDocument();
    });
  });

  test("clicking a search result redirects to a movie page", async () => {
    // Mock search returning one movie
    (global.fetch as jest.Mock).mockImplementationOnce(() =>
      mockFetch(["Test Movie (tt999)"])
    );
    delete window.location;
    window.location = { href: "" } as any;
    render(<App />);
    fireEvent.click(screen.getByText("Search"));
    fireEvent.change(screen.getByPlaceholderText("Search for movies..."), {
      target: { value: "Test" },
    });
    await waitFor(() => {
      expect(screen.getByText("Test Movie (tt999)")).toBeInTheDocument();
    });
    fireEvent.click(screen.getByText("Test Movie (tt999)"));
    // Expected redirection
    expect(window.location.href).toBe("/movie/tt999");
  });

  test("RecommendationsPage does not fetch recommendations when input is empty", () => {
    render(<App />);
    fireEvent.click(screen.getByText("Recommendations"));
    fireEvent.click(screen.getByText("Get Recommendations"));
    // Since input is empty, recommendations list should remain empty
    expect(
      screen.queryByText("Failed to fetch recommendations")
    ).not.toBeInTheDocument();
  });

  test("RecommendationsPage fetches recommendations on valid input", async () => {
    const mockRecData = {
      recommendations: ["Rec Movie 1", "Rec Movie 2"],
      genres: ["Drama", "Action"],
      imdb_id: ["tt101", "tt102"],
    };
    (global.fetch as jest.Mock).mockImplementationOnce(() =>
      mockFetch(mockRecData)
    );
    render(<App />);
    fireEvent.click(screen.getByText("Recommendations"));
    const input = screen.getByPlaceholderText(/Enter movies/i);
    fireEvent.change(input, { target: { value: "Movie X, Movie Y" } });
    fireEvent.click(screen.getByText("Get Recommendations"));
    await waitFor(() => {
      expect(screen.getByText("Rec Movie 1")).toBeInTheDocument();
      expect(screen.getByText("Rec Movie 2")).toBeInTheDocument();
    });
  });

  test("WatchlistPage shows login prompt if not logged in", () => {
    render(<App />);
    fireEvent.click(screen.getByText("Watchlist"));
    expect(
      screen.getByText("Please log in to use the watchlist.")
    ).toBeInTheDocument();
  });

  test("WatchlistPage fetches watchlist when logged in", async () => {
    const mockWatchlist = [
      { name: "Movie 1", imdb_id: "tt201", time: "10:00 AM" },
    ];
    (global.fetch as jest.Mock).mockImplementationOnce(() =>
      mockFetch(mockWatchlist)
    );
    // Render App with user logged in by simulating a successful login.
    render(<App />);
    // Simulate login by clicking logout button replacement for testing
    // (Assume that login updates the state and renders Watchlist)
    // For this test, directly click tab switching after setting state.
    fireEvent.click(screen.getByText("Login"));
    // Force user state change by clicking login (plugin our success mock)
    fireEvent.change(screen.getByPlaceholderText(/username/i), {
      target: { value: "user1" },
    });
    fireEvent.change(screen.getByPlaceholderText(/password/i), {
      target: { value: "secret" },
    });
    fireEvent.click(screen.getByText("Login"));
    await waitFor(() =>
      expect(screen.getByText("Watchlist")).toBeInTheDocument()
    );
    fireEvent.click(screen.getByText("Watchlist"));
    await waitFor(() =>
      expect(screen.getByText("Movie 1")).toBeInTheDocument()
    );
  });

  test("WatchedHistoryPage shows login prompt if not logged in", () => {
    render(<App />);
    fireEvent.click(screen.getByText("Watched History"));
    expect(
      screen.getByText("Please log in to use the watched history.")
    ).toBeInTheDocument();
  });

  test("WatchedHistoryPage adds to history with valid input", async () => {
    (global.fetch as jest.Mock).mockImplementationOnce(() =>
      mockFetch({ message: "Added" })
    );
    render(<App />);
    // Simulate login
    fireEvent.change(screen.getByPlaceholderText(/username/i), {
      target: { value: "user2" },
    });
    fireEvent.change(screen.getByPlaceholderText(/password/i), {
      target: { value: "secret" },
    });
    fireEvent.click(screen.getByText("Login"));
    await waitFor(() =>
      expect(screen.getByText("Watched History")).toBeInTheDocument()
    );
    fireEvent.click(screen.getByText("Watched History"));
    const movieInput = screen.getByPlaceholderText(/Enter movie name/i);
    const dateInput = screen.getByDisplayValue("");
    fireEvent.change(movieInput, { target: { value: "Movie History" } });
    fireEvent.change(dateInput, { target: { value: "2025-02-20" } });
    fireEvent.click(screen.getByText("Add to Watched History"));
    await waitFor(() =>
      expect(
        screen.getByText(/Movie added to Watched History/i)
      ).toBeInTheDocument()
    );
  });

  test("WallPage shows only reviews for guest", () => {
    render(<App />);
    fireEvent.click(screen.getByText("Wall"));
    // For guest user, we expect only recent reviews and a sign in prompt for posting
    expect(screen.getByText("Recent Reviews")).toBeInTheDocument();
    expect(screen.getByText("Sign in to Comment")).toBeInTheDocument();
  });

  test("WallPage allows logged-in user to post a comment", async () => {
    (global.fetch as jest.Mock)
      // First call: login
      .mockImplementationOnce(() => mockFetch({}))
      // Second call: posting comment
      .mockImplementationOnce(() => mockFetch({ message: "Posted" }));

    render(<App />);
    // Simulate login
    fireEvent.change(screen.getByPlaceholderText(/username/i), {
      target: { value: "user3" },
    });
    fireEvent.change(screen.getByPlaceholderText(/password/i), {
      target: { value: "secret" },
    });
    fireEvent.click(screen.getByText("Login"));
    await waitFor(() => expect(screen.getByText("Wall")).toBeInTheDocument());
    fireEvent.click(screen.getByText("Wall"));
    const commentInput = screen.getByPlaceholderText(
      "Write your comment here..."
    );
    fireEvent.change(commentInput, { target: { value: "Great movie!" } });
    const postButton = screen.getByText("Post Comment");
    expect(postButton).not.toBeDisabled();
    fireEvent.click(postButton);
    await waitFor(() =>
      expect(
        screen.getByText(/Your comment has been posted/i)
      ).toBeInTheDocument()
    );
  });

  test("FriendsPage shows login prompt when not logged in", () => {
    render(<App />);
    fireEvent.click(screen.getByText("Friends"));
    expect(
      screen.getByText("Please log in to use the friends feature.")
    ).toBeInTheDocument();
  });

  test("FriendsPage fetches friend list and allows adding a friend", async () => {
    const mockFriends = [["friend1"], ["friend2"]];
    (global.fetch as jest.Mock)
      // For add friend API
      .mockImplementationOnce(() => mockFetch({}))
      // For fetching friend list
      .mockImplementationOnce(() => mockFetch(mockFriends));

    render(<App />);
    // Simulate login
    fireEvent.change(screen.getByPlaceholderText(/username/i), {
      target: { value: "user4" },
    });
    fireEvent.change(screen.getByPlaceholderText(/password/i), {
      target: { value: "secret" },
    });
    fireEvent.click(screen.getByText("Login"));
    await waitFor(() =>
      expect(screen.getByText("Friends")).toBeInTheDocument()
    );
    fireEvent.click(screen.getByText("Friends"));
    // Add friend
    const friendInput = screen.getByPlaceholderText("Enter friend's username");
    fireEvent.change(friendInput, { target: { value: "newfriend" } });
    fireEvent.click(screen.getByText("Add Friend"));
    await waitFor(() =>
      expect(screen.getByText(/Friend added successfully/i)).toBeInTheDocument()
    );
    // Friend list should show friend1 and friend2 after mock fetch
    await waitFor(() =>
      expect(screen.getByText("friend1")).toBeInTheDocument()
    );
    expect(screen.getByText("friend2")).toBeInTheDocument();
  });

  test("RecommendationGenieTab fetches recommendations on query", async () => {
    const genieData = { recommendations: ["Magic Movie 1", "Magic Movie 2"] };
    (global.fetch as jest.Mock).mockImplementationOnce(() =>
      mockFetch(genieData)
    );
    render(<App />);
    fireEvent.click(screen.getByText("🔮 Recommendation Genie"));
    const genieInput = screen.getByPlaceholderText(
      "E.g., 'A sci-fi adventure with a deep storyline'"
    );
    fireEvent.change(genieInput, {
      target: { value: "sci-fi" },
    });
    fireEvent.click(screen.getByText("Ask the Genie"));
    await waitFor(() => {
      expect(screen.getByText("Magic Movie 1")).toBeInTheDocument();
      expect(screen.getByText("Magic Movie 2")).toBeInTheDocument();
    });
  });

  test("RecommendationGenieTab shows no recommendations on network error", async () => {
    (global.fetch as jest.Mock).mockImplementationOnce(() =>
      Promise.reject(new Error("Network error"))
    );
    render(<App />);
    fireEvent.click(screen.getByText("🔮 Recommendation Genie"));
    fireEvent.change(
      screen.getByPlaceholderText(
        "E.g., 'A sci-fi adventure with a deep storyline'"
      ),
      { target: { value: "mysterious" } }
    );
    fireEvent.click(screen.getByText("Ask the Genie"));
    await waitFor(() =>
      expect(screen.queryByText("Magic Picks for You:")).not.toBeInTheDocument()
    );
  });

  test("Dark mode toggles on checkbox change", () => {
    render(<App />);
    const darkToggle = screen.getByRole("checkbox");
    // Initially dark mode is off
    expect(document.documentElement.classList.contains("dark")).toBeFalsy();
    fireEvent.click(darkToggle);
    expect(document.documentElement.classList.contains("dark")).toBeTruthy();
    fireEvent.click(darkToggle);
    expect(document.documentElement.classList.contains("dark")).toBeFalsy();
  });

  test("Logout triggers API call and resets user state", async () => {
    // First call: user login, second call: logout
    (global.fetch as jest.Mock)
      .mockImplementationOnce(() => mockFetch({}))
      .mockImplementationOnce(() => mockFetch({}));
    render(<App />);
    // Simulate login
    fireEvent.change(screen.getByPlaceholderText(/username/i), {
      target: { value: "user5" },
    });
    fireEvent.change(screen.getByPlaceholderText(/password/i), {
      target: { value: "secret" },
    });
    fireEvent.click(screen.getByText("Login"));
    await waitFor(() => expect(screen.getByText("Logout")).toBeInTheDocument());
    // Open logout alert dialog
    fireEvent.click(screen.getByText("Logout"));
    fireEvent.click(screen.getByText("Continue"));
    await waitFor(() => expect(screen.getByText("Login")).toBeInTheDocument());
  });

  test("MoviePage fetches movie details based on URL", async () => {
    // Set a fake URL for the movie page test
    const fakeMovieData = {
      Title: "Test Movie",
      Year: "2025",
      Genre: "Action",
      Runtime: "120 min",
      Poster: "poster.jpg",
      Plot: "Test plot",
      Director: "Test Director",
      Actors: "Actor 1, Actor 2",
      imdbRating: "8.0",
    };
    (global.fetch as jest.Mock).mockImplementationOnce(() =>
      mockFetch(fakeMovieData)
    );
    // Overwrite window.location.pathname
    Object.defineProperty(window, "location", {
      value: { pathname: "/movie/tt777" },
      writable: true,
    });
    render(<App />);
    // MoviePage should show the movie details
    await waitFor(() =>
      expect(screen.getByText("Test Movie")).toBeInTheDocument()
    );
    expect(screen.getByText("2025 | Action | 120 min")).toBeInTheDocument();
  });

  test("MoviePage disables comment input when user is guest", () => {
    // Set fake URL so MoviePage renders
    Object.defineProperty(window, "location", {
      value: { pathname: "/movie/tt888" },
      writable: true,
    });
    render(<App />);
    fireEvent.click(screen.getByText("Search")); // Switch away from login to simulate guest mode
    fireEvent.click(screen.getByText("Wall"));
    const commentInput = screen.getByPlaceholderText(
      "Write your comment here..."
    );
    expect(commentInput).toBeDisabled();
  });
});


describe("FriendsPage Component", () => {
  beforeEach(() => {
    fetch.mockClear();
  });

  test("renders the component", () => {
    render(<FriendsPage user={mockUser} />);
    expect(screen.getByText("Add Friend")).toBeInTheDocument();
    expect(screen.getByText("Friends List")).toBeInTheDocument();
    expect(screen.getByText("Friend Activity")).toBeInTheDocument();
  });

test("shows login message for guests", () => {
    render(<FriendsPage user="guest" />);
    expect(screen.getByText("Please log in to use the friends feature.")).toBeInTheDocument();
  });

test("fetches and displays friends", async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockFriends,
    });

    render(<FriendsPage user={mockUser} />);

    await waitFor(() => expect(screen.getByText("friend1")).toBeInTheDocument());
    expect(screen.getByText("friend2")).toBeInTheDocument();
  });

test("handles fetch friends API failure", async () => {
    fetch.mockRejectedValueOnce(new Error("Failed to fetch"));

    render(<FriendsPage user={mockUser} />);

    await waitFor(() => expect(window.alert).toHaveBeenCalledWith("Backend API cannot be reached."));
  });

test("adds a friend successfully", async () => {
    fetch
      .mockResolvedValueOnce({ ok: true }) // Add Friend API
      .mockResolvedValueOnce({ ok: true, json: async () => mockFriends }); // Fetch Friends API after adding

    render(<FriendsPage user={mockUser} />);

    fireEvent.change(screen.getByPlaceholderText("Enter friend's username"), {
      target: { value: "newFriend" },
    });

    fireEvent.click(screen.getByText("Add Friend"));

    await waitFor(() => expect(fetch).toHaveBeenCalledTimes(2));
    expect(screen.getByText("friend1")).toBeInTheDocument();
    expect(screen.getByText("friend2")).toBeInTheDocument();
  });

test("handles add friend API error", async () => {
    fetch.mockRejectedValueOnce(new Error("Failed to fetch"));

    render(<FriendsPage user={mockUser} />);

    fireEvent.change(screen.getByPlaceholderText("Enter friend's username"), {
      target: { value: "newFriend" },
    });

    fireEvent.click(screen.getByText("Add Friend"));

    await waitFor(() => expect(window.alert).toHaveBeenCalledWith("Backend API cannot be reached."));
  });

test("fetches and displays friend activity", async () => {
    fetch
      .mockResolvedValueOnce({ ok: true, json: async () => mockFriends }) // Fetch Friends
      .mockResolvedValueOnce({ ok: true, json: async () => mockActivity }); // Fetch Friend Activity

    render(<FriendsPage user={mockUser} />);

    await waitFor(() => expect(screen.getByText("friend1")).toBeInTheDocument());

    fireEvent.click(screen.getByText("friend1"));

    await waitFor(() => expect(screen.getByText("Test Movie")).toBeInTheDocument());
  });

test("handles fetch friend activity API failure", async () => {
    fetch.mockRejectedValueOnce(new Error("Failed to fetch"));

    render(<FriendsPage user={mockUser} />);

    await waitFor(() => expect(screen.getByText("friend1")).toBeInTheDocument());

    fireEvent.click(screen.getByText("friend1"));

    await waitFor(() => expect(window.alert).toHaveBeenCalledWith("Backend API cannot be reached."));
  });
});

const mockMovies = ["Inception", "Interstellar", "The Dark Knight"];

describe("MovieSearchDropdown Component", () => {
  beforeEach(() => {
    fetch.mockClear();
  });

  test("renders input field with placeholder", () => {
    render(<MovieSearchDropdown placeholder="Search movies..." onSelect={jest.fn()} />);
    expect(screen.getByPlaceholderText("Search movies...")).toBeInTheDocument();
  });

test("does not search when input has less than 3 characters", async () => {
    render(<MovieSearchDropdown onSelect={jest.fn()} />);
    const input = screen.getByRole("textbox");

    fireEvent.change(input, { target: { value: "In" } });

    await waitFor(() => expect(fetch).not.toHaveBeenCalled());
  });

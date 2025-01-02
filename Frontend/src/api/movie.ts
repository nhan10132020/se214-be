import axios from "axios";

const backendURL = process.env.NEXT_PUBLIC_BACKEND_URL;

// Create Axios instance
const axiosInstance = axios.create({
  baseURL: backendURL, // Replace with your API base URL
  timeout: 10000, // Set a timeout (e.g., 10 seconds)
  headers: {
    "Content-Type": "application/json",
  },
});

export const getMovieDetail = async (id: string | string[]) => {
    try {
      const movie_detail = await axiosInstance.get(`/movies/${id}/detail`);
      const actors = await axiosInstance.get(`/movies/${id}/actors`);
      const genres = await axiosInstance.get(`/movies/${id}/genres`);

      // merge actors and genres into movie_detail
      movie_detail.data[0].actors = actors.data;
      movie_detail.data[0].genres = genres.data;
      return movie_detail.data[0];
    } catch (error) {
      console.error("Error fetching data:", error);
      return [];
    }
};

export const getMoveComment = async (id: string | string[]) => {
  try {
    const comments = await axiosInstance.get(`/movies/${id}/comments`);
    return comments.data;
  } catch (error) {
    console.error("Error fetching data:", error);
    return [];
  }
};
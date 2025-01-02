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

export const getAllGenres = async () => {
    try {
      const response = await axiosInstance.get("/genres");
      return response.data;
    } catch (error) {
      console.error("Error fetching data:", error);
      return [];
    }
  };

export const getAllMoviesByGerensID = async (id: string,page: number) => {
    try {
      const response = await axiosInstance.get(`/genres/${id}/movies?page=${page}`);
      return response.data;
    } catch (error) {
      console.error("Error fetching data:", error);
      return [];
    }
  };
  
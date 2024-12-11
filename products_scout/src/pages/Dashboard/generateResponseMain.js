// ===========================================Done=========================================================

import axios from "axios";

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL; // Use environment variable for the API base URL

/**
 * Generate a response based on the user's query.
 * This function uses the `/generate-response-main/` endpoint.
 * @param {string} query - The user's query.
 * @returns {Promise<Object>} - The response containing the generated response only.
 */
export const generateResponseMain = async (query) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/generate-response-main/`, { query });
        return {
            generatedResponse: response.data.response || "No response generated.", // Fallback for response
            status: response.data.status || "partial", // Indicates that it's a partial response
            message: response.data.message || "Processing additional details."
        };
    } catch (error) {
        console.error("Error generating response:", error);
        return {
            generatedResponse: "An error occurred while generating a response.", // Generic error message
            status: "error",
            message: "Failed to generate response."
        };
    }
};

/**
 * Fetch features and products based on the user's query.
 * This function uses the `/fetch-products-main/` endpoint.
 * @param {string} query - The user's query.
 * @returns {Promise<Object>} - The response containing extracted features and products.
 */
export const fetchFeaturesAndProductsMain = async (query) => {
    try {
        // Changed from GET to POST and included the query in the request body
        const response = await axios.post(`${API_BASE_URL}/fetch-products-main/`, { query });
        return {
            extractedFeatures: response.data.extracted_features || null, // Extracted features in JSON format
            products: response.data.products || [], // List of products
            status: response.data.status || "complete" // Indicates the processing is complete
        };
    } catch (error) {
        console.error("Error fetching features and products:", error);
        return {
            extractedFeatures: null, // Return null for features on error
            products: [], // Return an empty list of products on error
            status: "error"
        };
    }
};

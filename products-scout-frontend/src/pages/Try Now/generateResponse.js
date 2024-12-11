// ===========================================Done=========================================================

import axios from "axios";

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL; // Use environment variable for the API base URL

/**
 * Generate a response based on the user's query.
 * This function uses the `/generate-response/` endpoint.
 * @param {string} query - The user's query.
 * @returns {Promise<Object>} - The response containing generated response, extracted features, and products.
 */
export const generateResponse = async (query) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/generate-response/`, { query });
        return {
            generatedResponse: response.data.response || "No response generated.", // NEWLY ADDED: Fallback for response
            extractedFeatures: response.data.extracted_features || null, // Updated to return null instead of string
            products: response.data.products || []
        };
    } catch (error) {
        console.error("Error generating response:", error);
        return {
            generatedResponse: "An error occurred while generating a response.", // NEWLY ADDED: Generic error message
            extractedFeatures: null, // NEWLY ADDED: Return null for features on error
            products: []
        };
    }
};

/**
 * Check if a query or response is product-related.
 * This function uses the `/is-product-related/` endpoint.
 * @param {string} query - The user's query.
 * @param {string} response - The generated response.
 * @returns {Promise<boolean>} - True if product-related, otherwise false.
 */
export const isProductRelated = async (query, response) => {
    try {
        const res = await axios.post(`${API_BASE_URL}/is-product-related/`, { query, response });
        return res.data.is_product_related || false;
    } catch (error) {
        console.error("Error checking if product-related:", error);
        return false;
    }
};

/**
 * Fetch products based on extracted features.
 * This function uses the `/fetch-products/` endpoint.
 * @param {Object} features - The extracted features in JSON format.
 * @returns {Promise<Array>} - The list of products.
 */
export const fetchProducts = async (features) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/fetch-products/`, { features });
        return response.data || [];
    } catch (error) {
        console.error("Error fetching products:", error);
        return [];
    }
};

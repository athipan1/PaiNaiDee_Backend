# Frontend Error Handling Suggestion

This document provides a code snippet and explanation for implementing robust error handling in the frontend when making API calls to the PaiNaiDee backend.

## Problem

The frontend might not be handling API errors gracefully. If an API call fails (e.g., due to a network error, a server error, or a non-existent endpoint), the user might see a broken page or a confusing error message.

## Solution

Implement a wrapper function for the `fetch` API that handles errors consistently. This function should be used for all API calls to the backend.

### Example `fetch` Wrapper with Error Handling

Here is an example in JavaScript of a function that fetches data from the API and includes proper error handling.

```javascript
async function fetchApi(url, options = {}) {
  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json',
      // Add other default headers here, like Authorization
    },
  };

  const config = {
    ...defaultOptions,
    ...options,
    headers: {
      ...defaultOptions.headers,
      ...options.headers,
    },
  };

  try {
    const response = await fetch(url, config);

    if (!response.ok) {
      // Handle HTTP errors (e.g., 404, 500)
      let errorMessage = `HTTP error! status: ${response.status}`;
      try {
        const errorData = await response.json();
        errorMessage = errorData.message || errorData.detail || errorMessage;
      } catch (e) {
        // Could not parse error JSON
      }
      throw new Error(errorMessage);
    }

    // Handle successful response
    // Check if the response has content
    const contentType = response.headers.get("content-type");
    if (contentType && contentType.indexOf("application/json") !== -1) {
      return await response.json();
    } else {
      return; // No content
    }

  } catch (error) {
    // Handle network errors or errors thrown from the response handling
    console.error('API call failed:', error);
    // Here you can set a state to show a user-friendly error message
    // in your UI, like "Could not connect to the server."
    throw error; // Re-throw the error to be caught by the calling code
  }
}

// --- Example Usage ---

async function getAttractions() {
  try {
    const data = await fetchApi('/api/attractions');
    console.log('Attractions:', data);
    // Update your UI with the data
  } catch (error) {
    // Show an error message to the user
    const errorContainer = document.getElementById('error-container');
    if (errorContainer) {
      errorContainer.textContent = `Failed to load attractions: ${error.message}`;
    }
  }
}

// Example of calling a non-existent endpoint
async function testInvalidEndpoint() {
  try {
    await fetchApi('/api/non-existent-endpoint');
  } catch (error) {
    const errorContainer = document.getElementById('error-container');
    if (errorContainer) {
      errorContainer.textContent = `Error: ${error.message}`;
    }
  }
}
```

### How to Use

1.  **Add the `fetchApi` function** to a utility file in your frontend project.
2.  **Replace all direct `fetch` calls** to your backend with calls to `fetchApi`.
3.  **Add a UI element** (e.g., a div with `id="error-container"`) to your HTML to display error messages to the user.
4.  **Style the error container** to make it visible to the user (e.g., with a red background).

This approach will ensure that all API errors are handled consistently and that the user is always informed when something goes wrong.

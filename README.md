# Marriage Matchmaking App

## Overview
The Marriage Matchmaking App is a backend application designed to help users find potential matches based on their profile information. Users can create, read, update, and delete profiles with details such as name, age, gender, email, city, and interests. The application efficiently matches users based on shared interests using a bitmask representation, ensuring optimized storage and retrieval.

## API Documentation
The application exposes RESTful APIs for managing user profiles and finding matches.

### Base URL
```
http://localhost:8000
```

### Swagger UI
```
http://localhost:8000/docs
```

### API Endpoints

#### Create User
- **Endpoint:** `POST /users`
- **Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "gender": "M",
  "city": "New York",
  "interests": ["Running", "Cycling"]
}
```
- **Response:**
```json
{
  "user_id": 1,
  "message": "User created successfully."
}
```

#### Get All Users (Paginated)
- **Endpoint:** `GET /users?skip=0&limit=10`
- **Response:**
```json
{
  "users": [
    {
      "id": 1,
      "name": "John Doe",
      "email": "john@example.com",
      "gender": "M",
      "city": "New York",
      "interests": ["Running", "Cycling"]
    }
  ]
}
```

#### Get User by ID
- **Endpoint:** `GET /users/{user_id}`
- **Response:**
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "gender": "M",
  "city": "New York",
  "interests": ["Running", "Cycling"]
}
```

#### Update User Interests
- **Endpoint:** `PUT /users/{user_id}/interests/`
- **Request Body:**
```json
{
  "interests": ["Yoga", "Swimming"]
}
```
- **Response:**
```json
{
  "user_id": 1,
  "message": "User interests updated successfully."
}
```

#### Delete User
- **Endpoint:** `DELETE /users/{user_id}`
- **Response:**
```json
{
  "message": "User deleted successfully."
}
```

#### Find Matches for a User
- **Endpoint:** `GET /users/{user_id}/matches?limit=10`
- **Response:**
```json
{
  "matches": [
    {
      "candidate": {
        "id": 2,
        "name": "Jane Doe",
        "email": "jane@example.com",
        "gender": "F",
        "city": "Los Angeles",
        "interests": ["Running", "Cycling"]
      },
      "similarity": 2
    }
  ]
}
```

## Email Validation
- The application ensures valid email addresses using Pydantic's `EmailStr` validator.

## Thought Process & Implementation Evolution

### Initial Approach: Brute Force Matching
1. Initially considered allowing any user-defined interest as a string.
2. Realized that string-based matching is computationally expensive.
3. Inspired by platforms like Shaadi.com, adopted predefined interests.
![image](https://github.com/user-attachments/assets/76f81f3b-b555-408e-9838-5b429ef301bf)
![image](https://github.com/user-attachments/assets/c75619ad-e530-4104-8e2b-29cf68ea5b96)



### Optimized Storage: Bitmask Representation
1. Storing all interests in a database is inefficient.
2. Implemented bitmask encoding to reduce memory usage and enable fast operations.
4. currently only user details key as unqiue id is stored in redis with their details as values
(this improved lookup time from 34ms to 8ms increase in 74%)

### Efficient Matchmaking Algorithm
1. Users are prioritized based on shared interests.
2. Matches are fetched in decreasing order of common interests:
   - Exact interest matches first.
   - Followed by users with slightly differing interests.
   - If no matches, include other users as fallback.
3. This approach ensures an effective user experience.

## Future Scope & Challenges

### Frequent Database Access Issue
1. Initial approach required scanning the entire user table for matches.
2. Encountered performance issues due to full-table scans.

### Redis for Match Caching
1. To optimize, considered storing top matches per user in Redis.
2. Used key-value pairs where:
   - **Key**: Interest bitmask.
   - **Value**: Users sharing that interest.
3. Challenges:
   - Requires careful cache invalidation.
   - Updates must be synchronized efficiently.

### Kafka for Asynchronous Processing
1. Matchmaking can be offloaded to Kafka-based background processing.
2. Future implementation can leverage event-driven architecture for real-time updates.

## Conclusion
The current implementation provides an efficient, scalable matchmaking system. Future improvements, including Redis caching for matches and Kafka-based processing, will further enhance performance and scalability.

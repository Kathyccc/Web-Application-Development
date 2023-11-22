"use strict"
let loadPostURL

function initializeStream(url) {
    loadPostURL = url;
}

// Sends a new request to update the to-do list
function loadPosts() {
    let xhr = new XMLHttpRequest()
    xhr.onreadystatechange = function() {
        if (this.readyState !== 4) return
        updatePage(xhr)
    }

    xhr.open("GET", loadPostURL, true)
    xhr.send()
}

function updatePage(xhr) {
    if (xhr.status === 200) {
        let response = JSON.parse(xhr.responseText);
        updatePosts(response); 
        return;
    }

    if (xhr.status === 0) {
        displayError("Cannot connect to server");
        return;
    }

    if (!xhr.getResponseHeader('content-type') === 'application/json') {
        displayError(`Received status = ${xhr.status}`);
        return;
    }

    let response = JSON.parse(xhr.responseText);
    if (response.hasOwnProperty('error')) {
        displayError(response.error);
        return;
    }

    displayError(response);
}

function updatePosts(response) {
    let postsContainer = document.getElementById("my-posts-go-here")

    // Check if response.posts is empty
    if (response.comments && response.posts.length == 0 && response.comments.length > 0) {
        let post_id = response.comments[0].post_id
        let commentContainer = document.getElementById(`my-comments-go-here-for-post-${post_id}`)
        updateComments(response.comments, commentContainer)
        return 
    }

    for (let post of response.posts) {
        let comments = response.comments.filter(comment => comment.post_id === post.id);

        let existingPostElement = document.getElementById(`id_post_div_${post.id}`);

        if (existingPostElement) {
            let commentContainer = document.getElementById(`my-comments-go-here-for-post-${post.id}`)
            updateComments(comments, commentContainer)
        } else {
            let newPostElement = makePostElement(post, comments);
            postsContainer.prepend(newPostElement);
        }
    }
}

function updateComments(comments, CommentContainer) {
    for(let comment of comments) {
        let existingCommentElement = document.getElementById(`id_comment_div_${comment.id}`);

        if (!existingCommentElement) {
            let newCommentElement = document.createElement("div")
            newCommentElement.id = `id_comment_div_${comment.id}`
            newCommentElement.className = `comment-div`

            const creationTime = formatDateTime(comment.creation_time)
            
            newCommentElement.innerHTML = `
                <a href="/profile/${comment.creator.id}" id="id_comment_profile_${comment.id}">
                    Comment by ${sanitize(comment.creator.fname)} ${sanitize(comment.creator.lname)}
                </a>
                <p id="id_comment_text_${comment.id}">${sanitize(comment.text)}</p>
                <p id="id_comment_date_time_${comment.id}">${creationTime}</p>`;

            CommentContainer.appendChild(newCommentElement)
        }
    }
}

// Construct a post element
function makePostElement(post, comments) {
    let postElement = document.createElement("div");
    postElement.className = "post_div"
    postElement.id = `id_post_div_${post.id}`

    const creationTime = formatDateTime(post.creation_time)

    postElement.innerHTML = `
        <a href='/profile/${post.user.id}' id="id_post_profile_${post.id}">
            Post by ${sanitize(post.user.first_name)} ${sanitize(post.user.last_name)}
        </a>
        <p id="id_post_text_${post.id}">${sanitize(post.text)}</p>
        <p id="id_post_date_time_${post.id}">${creationTime}</p>`

    // Create comment container for this post
    let commentDiv = createCommentDiv(post, comments)
    postElement.appendChild(commentDiv);

    // Create a form for new comment
    let commentInputDiv = createCommentForm(post);
    postElement.appendChild(commentInputDiv);

    return postElement;
}

function createCommentDiv(post, comments) {
    let commentDiv = document.createElement("div");
    commentDiv.id = `my-comments-go-here-for-post-${post.id}`

    if (comments && comments.length > 0) {
        comments.forEach(comment => {
                let commentElement = document.createElement("div");
                commentElement.id = `id_comment_div_${comment.id}`
                commentElement.className = `comment-div`

                const creationTime = formatDateTime(comment.creation_time)

                commentElement.innerHTML = `
                    <a href="/profile/${comment.creator.id}" id="id_comment_profile_${comment.id}">
                        Comment by ${sanitize(comment.creator.fname)} ${sanitize(comment.creator.lname)}
                    </a>
                    <p id="id_comment_text_${comment.id}">${sanitize(comment.text)}</p>
                    <p id="id_comment_date_time_${comment.id}">${creationTime}</p>`
        
                commentDiv.appendChild(commentElement)
        })
    }

    return commentDiv
}

function createCommentForm(post) {
    const newCommentDiv = document.createElement("div")
    newCommentDiv.className = "commentForm"

    newCommentDiv.innerHTML = `
        <label>Comment:</label>
        <input type="text" id="id_comment_input_text_${post.id}" name="comment_text" required>
        <button type="submit" onclick="addComment(${post.id})" id="id_comment_button_${post.id}">Submit</button>`
    
    return newCommentDiv;
}

function displayError(message) {
    let errorElement = document.getElementById("error")
    if(!errorElement) {
        let errorElement_follower = document.getElementById("error-follower")
        errorElement_follower.innerHTML = message
    } else {
        errorElement.innerHTML = message
    }
}

function sanitize(s) {
    if (typeof s !== 'string') {
        console.error('sanitize was called with non-string argument:', s);
        return '';
    }
    // Be sure to replace ampersand first
    return s.replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
}

function addComment(post_id) {
    let commentTextElement = document.getElementById("id_comment_input_text_" + post_id)
    let commentTextValue   = commentTextElement.value

    // Clear input box and old error message (if any)
    commentTextElement.value = ''
    displayError('')

    let xhr = new XMLHttpRequest()
    xhr.onreadystatechange = function() {
        if (xhr.readyState !== 4) return
        updatePage(xhr) 
    }

    xhr.open("POST", "/socialnetwork/add-comment", true)
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded")
    xhr.send(`comment_text=${commentTextValue}&post_id=${post_id}&csrfmiddlewaretoken=${getCSRFToken()}`)
}

function getCSRFToken() {
    let cookies = document.cookie.split(";")
    for (let i = 0; i < cookies.length; i++) {
        let c = cookies[i].trim()
        if (c.startsWith("csrftoken=")) {
            return c.substring("csrftoken=".length, c.length)
        }
    }
    return "unknown"
}

function formatDateTime(isoDateTime) {
    const dateObj = new Date(isoDateTime);

    const dateOptions = { month: 'numeric', day: 'numeric', year: 'numeric' };
    const formattedDate = dateObj.toLocaleDateString(undefined, dateOptions);  // m/d/yyyy

    const timeOptions = { hour: 'numeric', minute: 'numeric', hour12: true };
    const formattedTime = dateObj.toLocaleTimeString(undefined, timeOptions);  // h:m A

    return `${formattedDate} ${formattedTime}`;
}




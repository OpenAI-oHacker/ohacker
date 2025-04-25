
import * as React from "react";
import { Navbar } from "@/components/Navbar";
import { PostCard } from "@/components/PostCard";
import { PostForm } from "@/components/PostForm";
import { DUMMY_POSTS, MOCK_USER, getRandomUser } from "@/data/dummyData";

export type CommentType = {
  id: number;
  user: { name: string; avatar?: string };
  text: string;
};
export type PostType = {
  id: number;
  user: { name: string; avatar?: string };
  image: string;
  caption: string;
  comments: CommentType[];
};

const Index: React.FC = () => {
  const [posts, setPosts] = React.useState<PostType[]>([]);
  const [showPostForm, setShowPostForm] = React.useState(false);

  React.useEffect(() => {
    const fetchFeed = async () => {
      try {
        const images_response = await fetch('http://127.0.0.1:8001/images');
        const images_data = await images_response.json();
        let comments_data = [];
        try {
          const comments_promises = images_data.images.map(image => 
            fetch(`http://127.0.0.1:8001/comments/${image}`)
              .then(response => response.json())
              .then(response => response.comments.map((comment, index) => ({
                id: `${image}-${index}`,
                user: getRandomUser(),
                text: comment.comment_text,
              })))
          );
          comments_data = await Promise.all(comments_promises);
        } catch (err) {
          console.error(err);
        }
        setPosts(images_data.images.map((image, index) => ({
          id: image,
          user: getRandomUser(),
          image: `http://127.0.0.1:8001/images/${image}`,
          caption: "",
          comments: comments_data[index] || [],
        }))); 
      } catch (err) {
        console.error('Error fetching feed:', err);
      } 
    };

    fetchFeed();
  }, []);

  const handleAddPost = async (post: PostType) => {
    const formData = new FormData();
    formData.append("base64_image", post.image);
    formData.append("caption", post.caption);
    const response = await fetch("http://127.0.0.1:8001/images", {
      method: "POST",
      body: formData
    })
    setPosts((prev) => [post, ...prev]);
  };

  const handleAddComment = async (postId: number, text: string) => {
    await fetch(`http://127.0.0.1:8001/comments/${postId}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        comment_text: text,
      })
    })

    const response = await fetch(`http://127.0.0.1:8001/comments/${postId}`)
    const data = await response.json()
    const serverComments = data.comments.map((comment, index) => ({
      id: `${postId}-${index}`,
      user: MOCK_USER,
      text: comment.comment_text,
    }))

    setPosts((prev) =>
      prev.map((p) =>
        p.id === postId
          ? {
              ...p,
              comments: serverComments.map((comment, index) => {
                const existingComment = p.comments.find(ec => ec.text === comment.text);
                return {
                  id: `${postId}-${index}`,
                  user: existingComment ? existingComment.user : MOCK_USER,
                  text: comment.text,
                }
              }),
            }
          : p
      )
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-pink-50 flex flex-col">
      <Navbar onNewPostClick={() => setShowPostForm(true)} />
      <main className="flex-grow flex flex-col items-center pt-7 px-2">
        <PostForm
          open={showPostForm}
          onClose={() => setShowPostForm(false)}
          onAddPost={handleAddPost}
        />
        {posts.length === 0 ? (
          <div className="text-center mt-16 text-lg text-gray-500">
            There are no posts yet.
          </div>
        ) : (
          <div className="flex flex-col w-full max-w-xl">
            {posts.map((post) => (
              <PostCard
                key={post.id}
                post={post}
                onAddComment={handleAddComment}
              />
            ))}
          </div>
        )}
      </main>
      <footer className="py-8 text-center text-sm text-gray-300 mt-8">
        © {new Date().getFullYear()} Instagram. Demo for Lovable.
      </footer>
    </div>
  );
};

export default Index;

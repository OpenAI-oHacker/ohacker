
import * as React from "react";
import { Navbar } from "@/components/Navbar";
import { PostCard } from "@/components/PostCard";
import { PostForm } from "@/components/PostForm";
import { DUMMY_POSTS, MOCK_USER } from "@/data/dummyData";

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
  const [posts, setPosts] = React.useState<PostType[]>(() =>
    DUMMY_POSTS.map((p) => ({
      ...p,
      comments: [...p.comments],
    }))
  );
  const [showPostForm, setShowPostForm] = React.useState(false);

  const handleAddPost = (post: PostType) => {
    setPosts((prev) => [post, ...prev]);
  };

  const handleAddComment = (postId: number, text: string) => {
    setPosts((prev) =>
      prev.map((p) =>
        p.id === postId
          ? {
              ...p,
              comments: [
                ...p.comments,
                {
                  id: Date.now(),
                  user: MOCK_USER,
                  text,
                },
              ],
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

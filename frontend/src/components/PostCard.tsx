
import * as React from "react";
import { User } from "lucide-react";
import { CommentSection } from "@/components/CommentSection";

interface Comment {
  id: number;
  user: { name: string; avatar?: string };
  text: string;
}
interface UserObj {
  name: string;
  avatar?: string;
}
interface PostData {
  id: number;
  user: UserObj;
  image: string;
  caption: string;
  comments: Comment[];
}

interface PostCardProps {
  post: PostData;
  onAddComment: (postId: number, text: string) => void;
}

export const PostCard: React.FC<PostCardProps> = ({ post, onAddComment }) => {
  return (
    <div className="bg-white/90 mb-4 max-w-[465px] w-full mx-auto border border-gray-200"> {/* mb-4 replaces mb-8 for less space; no rounded classes */}
      <div className="flex items-center gap-3 px-5 pt-4">
        {post.user.avatar ? (
          <img src={post.user.avatar} alt={post.user.name} className="w-10 h-10 border border-gray-200 object-cover shadow-sm" />
        ) : (
          <span className="w-10 h-10 bg-white border border-gray-200 flex items-center justify-center">
            <User className="text-neutral-400" size={22} />
          </span>
        )}
        <span className="font-semibold text-neutral-800 text-base">{post.user.name}</span>
      </div>
      <div className="w-full flex justify-center mt-3">
        <img
          src={post.image}
          alt={post.caption}
          className="w-full h-[300px] md:h-[400px] object-cover border-t border-gray-200" // removed rounded-xl
          style={{ objectPosition: "center" }}
        />
      </div>
      <div className="px-5 py-3">
        <p className="text-neutral-900 font-medium mb-2">{post.caption}</p>
        <CommentSection
          comments={post.comments}
          onAddComment={(text) => onAddComment(post.id, text)}
        />
      </div>
    </div>
  );
};

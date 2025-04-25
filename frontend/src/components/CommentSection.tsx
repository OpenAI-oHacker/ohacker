import * as React from "react";
import { MOCK_USER } from "@/data/dummyData";
import { User } from "lucide-react";
import { Input } from "@/components/ui/input";
import { toast } from "@/hooks/use-toast";

interface Comment {
  id: number;
  user: { name: string; avatar?: string };
  text: string;
}

interface CommentSectionProps {
  comments: Comment[];
  onAddComment: (text: string) => void;
}

export const CommentSection: React.FC<CommentSectionProps> = ({
  comments,
  onAddComment,
}) => {
  const [text, setText] = React.useState("");

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!text.trim()) {
      toast({
        title: "Type something to comment!",
        variant: "destructive",
      });
      return;
    }
    onAddComment(text.trim());
    setText("");
  }

  return (
    <div className="mt-2">
      <div className="flex flex-col gap-2 mb-1">
        {comments.map((c) => (
          <div key={c.id} className="flex items-start gap-2 group">
            {c.user.avatar ? (
              <img
                src={c.user.avatar}
                className="w-7 h-7 rounded-full mt-1 border border-gray-200 object-cover shadow-sm"
                alt={c.user.name}
              />
            ) : (
              <div className="w-7 h-7 rounded-full bg-white border border-gray-200 flex items-center justify-center mt-1 shadow-sm">
                <User size={16} className="text-neutral-400" />
              </div>
            )}
            <div className="flex flex-col rounded-xl px-3 py-1.5 bg-gray-50 border border-gray-200 group-hover:bg-neutral-100 group-hover:text-neutral-900 transition shadow max-w-xs md:max-w-sm text-neutral-900">
              <span className="font-semibold text-xs text-neutral-800">{c.user.name}</span>
              <span className="text-[0.97em]">{c.text}</span>
            </div>
          </div>
        ))}
      </div>
      <form
        onSubmit={handleSubmit}
        className="flex items-center gap-2 mt-2"
        autoComplete="off"
      >
        <Input
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Add a comment…"
          className="w-full text-[0.97em] rounded-lg bg-gray-50 border border-gray-200 text-neutral-800 placeholder:text-neutral-400"
        />
        <button
          type="submit"
          className="transition px-3 py-1.5 rounded-lg font-semibold text-white bg-neutral-900 border border-gray-200 hover:bg-neutral-100 hover:text-neutral-900"
        >
          Post
        </button>
      </form>
    </div>
  );
};

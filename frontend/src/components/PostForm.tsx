import * as React from "react";
import { MOCK_USER } from "@/data/dummyData";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";
import { toast } from "@/hooks/use-toast";

interface PostFormProps {
  open: boolean;
  onClose: () => void;
  onAddPost: (post: any) => void;
}

export const PostForm: React.FC<PostFormProps> = ({ open, onClose, onAddPost }) => {
  const [file, setFile] = React.useState<File | null>(null);
  const [caption, setCaption] = React.useState("");
  const [preview, setPreview] = React.useState<string>("");
  const [submitting, setSubmitting] = React.useState(false);

  // Handle file drop or selection
  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    if (e.target.files && e.target.files[0]) {
      const selected = e.target.files[0];
      setFile(selected);
      setPreview(URL.createObjectURL(selected));
    }
  }

  function handleDrop(e: React.DragEvent<HTMLDivElement>) {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const dropped = e.dataTransfer.files[0];
      setFile(dropped);
      setPreview(URL.createObjectURL(dropped));
    }
  }

  function handleDragOver(e: React.DragEvent<HTMLDivElement>) {
    e.preventDefault();
  }

  function handleImageRemove() {
    setFile(null);
    setPreview("");
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!file || !caption.trim()) {
      toast({
        title: "Please add an image and caption",
        description: "Both fields are required to create a post.",
        variant: "destructive",
      });
      return;
    }
    setSubmitting(true);
    const reader = new FileReader();
    reader.onloadend = () => {
      onAddPost({
        id: Date.now(),
        user: MOCK_USER,
        image: reader.result,
        caption: caption.trim(),
        comments: [],
      });
      setFile(null);
      setCaption("");
      setPreview("");
      setSubmitting(false);
      toast({
        title: "Post created!",
        description: "Your post has been added to the feed.",
      });
      onClose();
    };
    reader.readAsDataURL(file);
  }

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="rounded-xl shadow-xl bg-white/95 border border-gray-200 backdrop-blur-md">
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle className="text-neutral-900">Create New Post</DialogTitle>
          </DialogHeader>
          <div className="flex flex-col gap-4 py-2">
            <div
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              className={
                "flex flex-col items-center justify-center border-2 border-dashed border-gray-300 rounded-xl p-6 bg-gray-50 text-neutral-500 cursor-pointer transition hover:bg-neutral-100 hover:text-neutral-800"
              }
              tabIndex={0}
              onClick={() => document.getElementById("fileUploadInput")?.click()}
              style={{ outline: "none" }}
            >
              {preview ? (
                <div className="flex flex-col items-center">
                  <img
                    src={preview}
                    alt="Preview"
                    className="max-h-48 rounded mb-2 border border-gray-200"
                  />
                  <button
                    type="button"
                    onClick={handleImageRemove}
                    className="text-xs bg-neutral-900 text-white py-1 px-3 rounded hover:bg-neutral-100 hover:text-neutral-900 border border-gray-200 mb-2"
                  >
                    Remove
                  </button>
                </div>
              ) : (
                <span className="font-semibold text-base">
                  Drag and drop image or <span className="underline">click to upload</span>
                </span>
              )}
              <input
                id="fileUploadInput"
                type="file"
                accept="image/*"
                onChange={handleFileChange}
                style={{ display: "none" }}
              />
            </div>
            <label>
              <span className="font-semibold text-sm mb-1 text-neutral-700">Caption</span>
              <Textarea
                rows={3}
                placeholder="Say something about this photo..."
                value={caption}
                onChange={(e) => setCaption(e.target.value)}
                required
                className="text-neutral-900 border border-gray-200 bg-gray-50 rounded"
              />
            </label>
          </div>
          <DialogFooter className="mt-3 flex gap-2 justify-end">
            <button
              type="button"
              className="px-4 py-2 bg-white border border-gray-200 rounded text-neutral-600 hover:bg-neutral-100 hover:text-neutral-900 transition"
              onClick={onClose}
              disabled={submitting}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-neutral-900 text-white rounded border border-gray-200 hover:bg-neutral-100 hover:text-neutral-900 transition"
              disabled={submitting}
            >
              {submitting ? "Posting..." : "Post"}
            </button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};

import { Editor } from '@tiptap/react';
import { Bold, Italic, Heading2, Heading3, List, ListOrdered, Quote, Code, Image as ImageIcon, Undo, Redo } from 'lucide-react';

interface EditorToolbarProps {
    editor: Editor | null;
    onImageUpload: (file: File) => Promise<string>;
}

export function EditorToolbar({ editor, onImageUpload }: EditorToolbarProps) {
    if (!editor) return null;

    const handleImageClick = () => {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = 'image/*';
        input.onchange = async (e) => {
            const file = (e.target as HTMLInputElement).files?.[0];
            if (file) {
                try {
                    const url = await onImageUpload(file);
                    editor.chain().focus().setImage({ src: url }).run();
                } catch (error) {
                    console.error("Image upload failed", error);
                    alert("Lỗi upload ảnh. Vui lòng thử lại.");
                }
            }
        };
        input.click();
    };

    return (
        <div className="flex flex-wrap items-center gap-1 p-2 border-b border-gray-700 bg-[#161b22] rounded-t-lg">
            <button
                type="button"
                onClick={() => editor.chain().focus().toggleBold().run()}
                className={`p-1.5 rounded hover:bg-gray-700 transition-colors ${editor.isActive('bold') ? 'bg-green-900/40 text-green-500' : 'text-gray-400'}`}
                title="In đậm"
            >
                <Bold size={18} />
            </button>
            <button
                type="button"
                onClick={() => editor.chain().focus().toggleItalic().run()}
                className={`p-1.5 rounded hover:bg-gray-700 transition-colors ${editor.isActive('italic') ? 'bg-green-900/40 text-green-500' : 'text-gray-400'}`}
                title="In nghiêng"
            >
                <Italic size={18} />
            </button>

            <div className="w-px h-6 bg-gray-700 mx-1"></div>

            <button
                type="button"
                onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
                className={`p-1.5 rounded hover:bg-gray-700 transition-colors ${editor.isActive('heading', { level: 2 }) ? 'bg-green-900/40 text-green-500' : 'text-gray-400'}`}
                title="Heading 2"
            >
                <Heading2 size={18} />
            </button>
            <button
                type="button"
                onClick={() => editor.chain().focus().toggleHeading({ level: 3 }).run()}
                className={`p-1.5 rounded hover:bg-gray-700 transition-colors ${editor.isActive('heading', { level: 3 }) ? 'bg-green-900/40 text-green-500' : 'text-gray-400'}`}
                title="Heading 3"
            >
                <Heading3 size={18} />
            </button>

            <div className="w-px h-6 bg-gray-700 mx-1"></div>

            <button
                type="button"
                onClick={() => editor.chain().focus().toggleBulletList().run()}
                className={`p-1.5 rounded hover:bg-gray-700 transition-colors ${editor.isActive('bulletList') ? 'bg-green-900/40 text-green-500' : 'text-gray-400'}`}
                title="Danh sách trích ngang"
            >
                <List size={18} />
            </button>
            <button
                type="button"
                onClick={() => editor.chain().focus().toggleOrderedList().run()}
                className={`p-1.5 rounded hover:bg-gray-700 transition-colors ${editor.isActive('orderedList') ? 'bg-green-900/40 text-green-500' : 'text-gray-400'}`}
                title="Danh sách số"
            >
                <ListOrdered size={18} />
            </button>

            <div className="w-px h-6 bg-gray-700 mx-1"></div>

            <button
                type="button"
                onClick={() => editor.chain().focus().toggleBlockquote().run()}
                className={`p-1.5 rounded hover:bg-gray-700 transition-colors ${editor.isActive('blockquote') ? 'bg-green-900/40 text-green-500' : 'text-gray-400'}`}
                title="Trích dẫn"
            >
                <Quote size={18} />
            </button>
            <button
                type="button"
                onClick={() => editor.chain().focus().toggleCodeBlock().run()}
                className={`p-1.5 rounded hover:bg-gray-700 transition-colors ${editor.isActive('codeBlock') ? 'bg-green-900/40 text-green-500' : 'text-gray-400'}`}
                title="Đoạn mã (Code)"
            >
                <Code size={18} />
            </button>

            <div className="w-px h-6 bg-gray-700 mx-1"></div>

            <button
                type="button"
                onClick={handleImageClick}
                className="p-1.5 rounded hover:bg-gray-700 transition-colors text-gray-400"
                title="Chèn ảnh (Có thể kéo thả trực tiếp)"
            >
                <ImageIcon size={18} />
            </button>

            <div className="flex-1"></div>

            <button
                type="button"
                onClick={() => editor.chain().focus().undo().run()}
                disabled={!editor.can().undo()}
                className="p-1.5 rounded hover:bg-gray-700 transition-colors text-gray-400 disabled:opacity-30"
                title="Hoàn tác (Ctrl+Z)"
            >
                <Undo size={18} />
            </button>
            <button
                type="button"
                onClick={() => editor.chain().focus().redo().run()}
                disabled={!editor.can().redo()}
                className="p-1.5 rounded hover:bg-gray-700 transition-colors text-gray-400 disabled:opacity-30"
                title="Làm lại (Ctrl+Y)"
            >
                <Redo size={18} />
            </button>
        </div>
    );
}

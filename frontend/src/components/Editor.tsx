'use client';

import React, { useEffect, useState, useCallback } from 'react';
import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import Image from '@tiptap/extension-image';
import Placeholder from '@tiptap/extension-placeholder';
import { EditorToolbar } from './EditorToolbar';
import { uploadImageR2 } from '@/lib/api';

interface EditorProps {
    content: string;
    onChange: (html: string) => void;
    placeholder?: string;
    adminToken?: string;
}

export default function RichTextEditor({ content, onChange, placeholder = 'Viết nội dung...', adminToken }: EditorProps) {
    const [isUploading, setIsUploading] = useState(false);

    const handleImageUpload = useCallback(async (file: File): Promise<string> => {
        if (!adminToken) throw new Error("Missing admin token");
        setIsUploading(true);
        try {
            const url = await uploadImageR2(file, adminToken);
            return url;
        } finally {
            setIsUploading(false);
        }
    }, [adminToken]);

    const editor = useEditor({
        extensions: [
            StarterKit,
            Image.configure({
                HTMLAttributes: {
                    class: 'rounded-md max-w-full h-auto mt-4',
                },
            }),
            Placeholder.configure({
                placeholder,
            }),
        ],
        content,
        immediatelyRender: false,
        editorProps: {
            attributes: {
                class: 'prose prose-invert prose-emerald min-w-full min-h-[400px] p-4 focus:outline-none bg-[#0d1117] rounded-b-lg border-x border-b border-gray-700',
            },
            handlePaste: (view, event, slice) => {
                const items = event.clipboardData?.items;
                if (!items) return false;

                for (const item of Array.from(items)) {
                    if (item.type.indexOf('image') === 0) {
                        event.preventDefault();
                        const file = item.getAsFile();
                        if (file) {
                            handleImageUpload(file).then(url => {
                                const { schema } = view.state;
                                const node = schema.nodes.image.create({ src: url });
                                const transaction = view.state.tr.replaceSelectionWith(node);
                                view.dispatch(transaction);
                            }).catch(e => {
                                console.error("Lỗi upload ảnh dán:", e);
                                alert("Upload ảnh thất bại.");
                            });
                            return true;
                        }
                    }
                }
                return false;
            },
            handleDrop: (view, event, slice, moved) => {
                if (!moved && event.dataTransfer && event.dataTransfer.files && event.dataTransfer.files[0]) {
                    const file = event.dataTransfer.files[0];
                    if (file.type.indexOf('image') === 0) {
                        event.preventDefault();
                        const coordinates = view.posAtCoords({ left: event.clientX, top: event.clientY });

                        handleImageUpload(file).then(url => {
                            if (coordinates) {
                                const { schema } = view.state;
                                const node = schema.nodes.image.create({ src: url });
                                const transaction = view.state.tr.insert(coordinates.pos, node);
                                view.dispatch(transaction);
                            }
                        }).catch(e => {
                            console.error("Lỗi upload ảnh kéo thả:", e);
                            alert("Upload ảnh thất bại.");
                        });
                        return true;
                    }
                }
                return false;
            }
        },
        onUpdate: ({ editor }) => {
            onChange(editor.getHTML());
        },
    });

    // Sync content conditionally (e.g. from parent loaded data)
    useEffect(() => {
        if (editor && content && content !== editor.getHTML()) {
            editor.commands.setContent(content);
        }
    }, [content, editor]);

    return (
        <div className="relative flex flex-col w-full">
            <EditorToolbar editor={editor} onImageUpload={handleImageUpload} />
            <div className="relative focus-within:ring-1 focus-within:ring-green-500/50 transition-all rounded-b-lg">
                {isUploading && (
                    <div className="absolute top-2 right-2 z-10 bg-black/80 text-green-500 text-xs px-2 py-1 rounded-md flex items-center gap-2 border border-green-900 shadow-md">
                        <span className="w-3 h-3 border-2 border-green-500 border-t-transparent rounded-full animate-spin"></span>
                        Đang tải ảnh lên R2...
                    </div>
                )}
                <EditorContent editor={editor} />
            </div>
            <style jsx global>{`
        /* Minimal styling for placeholder */
        .tiptap p.is-editor-empty:first-child::before {
          content: attr(data-placeholder);
          float: left;
          color: #8b949e;
          pointer-events: none;
          height: 0;
        }
      `}</style>
        </div>
    );
}

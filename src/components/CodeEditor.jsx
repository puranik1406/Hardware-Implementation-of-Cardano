import { useState, useRef, useEffect } from 'react'
import { EditorView, basicSetup } from 'codemirror'
import { EditorState } from '@codemirror/state'
import { cpp } from '@codemirror/lang-cpp'
import { oneDark } from '@codemirror/theme-one-dark'

const CodeEditor = ({ code, onChange, language = 'cpp' }) => {
  const editorRef = useRef(null)
  const viewRef = useRef(null)

  useEffect(() => {
    if (!editorRef.current) return

    const extensions = [
      basicSetup,
      cpp(),
      oneDark,
      EditorView.theme({
        '&': {
          height: '300px',
          fontSize: '14px',
          fontFamily: 'Fira Code, Monaco, Cascadia Code, monospace'
        },
        '.cm-content': {
          padding: '12px',
          minHeight: '280px'
        },
        '.cm-focused': {
          outline: '2px solid #00979D'
        },
        '.cm-scroller': {
          fontFamily: 'Fira Code, Monaco, Cascadia Code, monospace'
        }
      }),
      EditorView.updateListener.of((update) => {
        if (update.docChanged) {
          onChange(update.state.doc.toString())
        }
      })
    ]

    const state = EditorState.create({
      doc: code,
      extensions
    })

    const view = new EditorView({
      state,
      parent: editorRef.current
    })

    viewRef.current = view

    return () => {
      view.destroy()
    }
  }, [])

  useEffect(() => {
    if (viewRef.current && viewRef.current.state.doc.toString() !== code) {
      const transaction = viewRef.current.state.update({
        changes: {
          from: 0,
          to: viewRef.current.state.doc.length,
          insert: code
        }
      })
      viewRef.current.dispatch(transaction)
    }
  }, [code])

  return (
    <div className="border border-gray-600 rounded-lg overflow-hidden bg-gray-900">
      <div ref={editorRef} className="code-editor" />
    </div>
  )
}

export default CodeEditor
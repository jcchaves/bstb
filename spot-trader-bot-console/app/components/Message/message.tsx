import { MessageProps } from "@/app/types/components/message";
import { useEffect, useRef } from "react";

export default function Message({ text, visible, onClose }: MessageProps) {

    const backdropRef = useRef(null)
    const modalDialogRef = useRef(null)

    useEffect(() => {
        console.log("Mounted message....")
        if (backdropRef != null && backdropRef.current != null) {
            console.log(backdropRef.current)
            backdropRef.current.style.display = "none"
            modalDialogRef.current.style.display = "none"
            backdropRef.current.addEventListener("transitionend", (event) => {
                console.log("transition ended...")
                if (backdropRef.current.style.display == "block" && !backdropRef.current.classList.contains("show")) {
                    backdropRef.current.style.display = "none"
                    modalDialogRef.current.style.display = "none"
                }
            }, true)
            backdropRef.current.addEventListener("transitionrun", (event) => {
                console.log("transition run...")
            }, true);
            backdropRef.current.addEventListener("transitionstart", (event) => {
                console.log("transition start...")
            }, true);
        }
    }, [])

    useEffect(() => {
        console.log(`Changed to ${visible ? "visible" : "hidden"}`)
        if (visible) {
            backdropRef.current.style.display = "block"
            modalDialogRef.current.style.display = "block"
            window.setTimeout(function () {
                backdropRef.current.classList.add("show")
                modalDialogRef.current.classList.add("show")
            }, 0); // do this asap 

        } else {
            backdropRef.current.classList.remove("show");
            modalDialogRef.current.classList.remove("show");

        }
    }, [visible])

    function checkStuff() {
        if (backdropRef != null && backdropRef.current != null) {
            console.log(backdropRef.current)
            console.log(backdropRef.current.style.display)
        }
    }

    return (
        <div>
            <div ref={modalDialogRef} className="modal fade" tabIndex="-1">
                <div className="modal-dialog">
                    <div className="modal-content">
                        <div className="modal-header">
                            <button type="button" className="btn-close" data-bs-dismiss="modal" aria-label="Close" onClick={onClose}></button>
                        </div>
                        <div className="modal-body">
                            <p>{text}</p>
                        </div>
                        <div className="modal-footer">
                            <button type="button" className="btn btn-secondary" data-bs-dismiss="modal" onClick={checkStuff}>Close</button>
                        </div>
                    </div>
                </div>
            </div>
            <div ref={backdropRef} className="modal-backdrop fade"></div>
        </div>)
}
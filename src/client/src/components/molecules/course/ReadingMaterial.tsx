import Markdown from "react-markdown";
import classes from "./ReadingMaterial.module.css";

interface ReadingMaterialProps {
    children: string;
}

export const ReadingMaterial = ({ children }: ReadingMaterialProps) => {
    return <Markdown className={classes.markdown}>{children}</Markdown>;
};

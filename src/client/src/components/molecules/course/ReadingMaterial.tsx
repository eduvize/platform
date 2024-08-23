import Markdown from "react-markdown";

interface ReadingMaterialProps {
    children: string;
}

export const ReadingMaterial = ({ children }: ReadingMaterialProps) => {
    return <Markdown>{children}</Markdown>;
};

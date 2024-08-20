export interface ToolCall {
    tool_name: string;
    arguments: any;
}

export interface ChatMessageDto {
    is_user: boolean;
    content: string;
    create_at_utc: string;
    tool_calls?: ToolCall[];
}

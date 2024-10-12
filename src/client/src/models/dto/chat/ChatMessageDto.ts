export interface ToolCall {
    tool_name: string;
    arguments: any;
}

export interface ChatMessageDto {
    id: string;
    is_user: boolean;
    content: string;
    user_id?: string;
    instructor_id?: string;
    create_at_utc: string;
    tool_calls?: ToolCall[];
}

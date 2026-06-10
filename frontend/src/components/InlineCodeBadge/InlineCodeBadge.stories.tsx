import type { Meta, StoryObj } from "@storybook/react";
import { InlineCodeBadge } from ".";

const meta: Meta<typeof InlineCodeBadge> = {
  title: "Atoms/InlineCodeBadge",
  component: InlineCodeBadge,
  parameters: { layout: "centered" },
  tags: ["autodocs"],
};
export default meta;

type Story = StoryObj<typeof InlineCodeBadge>;

export const Default: Story = { args: { children: "ANTHROPIC_API_KEY" } };
export const Copyable: Story = { args: { children: "SUPABASE_URL", copyable: true } };

export const InContext: Story = {
  render: () => (
    <p style={{ fontSize: "14px", color: "var(--color-text-primary)", lineHeight: "1.6", maxWidth: "400px" }}>
      Setze die Umgebungsvariable{" "}
      <InlineCodeBadge copyable>ANTHROPIC_API_KEY</InlineCodeBadge>{" "}
      in deiner <InlineCodeBadge>.env</InlineCodeBadge>-Datei.
    </p>
  ),
};

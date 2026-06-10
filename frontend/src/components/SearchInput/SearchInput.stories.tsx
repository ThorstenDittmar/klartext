import { useState } from "react";
import type { Meta, StoryObj } from "@storybook/react";
import { SearchInput } from ".";

const meta: Meta<typeof SearchInput> = {
  title: "Molecules/SearchInput",
  component: SearchInput,
  parameters: { layout: "centered" },
  tags: ["autodocs"],
};
export default meta;

type Story = StoryObj<typeof SearchInput>;

function Controlled(args: Partial<React.ComponentProps<typeof SearchInput>>) {
  const [value, setValue] = useState("");
  return (
    <div style={{ width: "280px" }}>
      <SearchInput value={value} onChange={setValue} {...args} />
    </div>
  );
}

export const Empty: Story = {
  render: () => <Controlled placeholder="Szene suchen…" />,
};

export const WithValue: Story = {
  render: () => {
    const [value, setValue] = useState("Held");
    return (
      <div style={{ width: "280px" }}>
        <SearchInput value={value} onChange={setValue} placeholder="Szene suchen…" />
      </div>
    );
  },
};

export const Inline: Story = {
  render: () => (
    <div
      style={{
        width: "280px",
        background: "var(--color-bg-subtle)",
        padding: "8px",
        borderRadius: "8px",
      }}
    >
      <Controlled variant="inline" placeholder="Filtern…" />
    </div>
  ),
};

export const Disabled: Story = {
  render: () => (
    <div style={{ width: "280px" }}>
      <SearchInput value="" onChange={() => {}} placeholder="Nicht verfügbar" disabled />
    </div>
  ),
};

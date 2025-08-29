import React from 'react';

const TestPage: React.FC = () => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="text-center space-y-4">
        <h1 className="text-4xl font-bold">Test Page</h1>
        <p className="text-lg text-muted-foreground">
          This is a test page to check if routing is working properly.
        </p>
        <p className="text-sm text-muted-foreground">
          If you can see this without refreshing, routing is working!
        </p>
      </div>
    </div>
  );
};

export default TestPage;
